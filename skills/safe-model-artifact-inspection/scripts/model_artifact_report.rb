#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "optparse"
require "pathname"
require "set"
require "timeout"

CONFIG_FILES = %w[
  config.json
  generation_config.json
  tokenizer_config.json
  special_tokens_map.json
  tokenizer.json
].freeze

SAFE_REPLACEMENTS = {
  "<" => "\\x3c",
  ">" => "\\x3e",
  "|" => "\\x7c",
  "{" => "\\x7b",
  "}" => "\\x7d"
}.freeze

PLACEHOLDER_NAMES = {
  "bos_token" => "BOS_TOKEN",
  "eos_token" => "EOS_TOKEN",
  "pad_token" => "PAD_TOKEN",
  "unk_token" => "UNK_TOKEN"
}.freeze

options = {
  format: "both",
  probes: true,
  probe_timeout: 30
}

parser = OptionParser.new do |opts|
  opts.banner = "usage: ruby scripts/model_artifact_report.rb MODEL_DIR [--format markdown|json|both] [--no-probes] [--probe-timeout SECONDS]"
  opts.on("--format FORMAT", "markdown, json, or both") { |value| options[:format] = value }
  opts.on("--no-probes", "skip ONNX runtime probes") { options[:probes] = false }
  opts.on("--probe-timeout SECONDS", Integer, "bounded runtime probe timeout") { |value| options[:probe_timeout] = value }
end

parser.parse!

model_dir = ARGV.shift
abort parser.to_s unless model_dir
abort "unsupported format: #{options[:format]}" unless %w[markdown json both].include?(options[:format])
abort "model directory does not exist: #{model_dir}" unless Dir.exist?(model_dir)

def read_json(path)
  return nil unless path && File.file?(path)

  JSON.parse(File.read(path))
rescue JSON::ParserError => e
  { "__parse_error__" => e.message }
end

def relative_path(model_dir, path)
  return nil unless path

  Pathname.new(path).relative_path_from(Pathname.new(model_dir)).to_s
end

def safe_string(value)
  value.to_s.encode("UTF-8", invalid: :replace, undef: :replace, replace: "\uFFFD").dump[1...-1].then do |text|
    SAFE_REPLACEMENTS.reduce(text) { |memo, (raw, escaped)| memo.gsub(raw, escaped) }
  end
end

def byte_array(value)
  value.to_s.encode("UTF-8", invalid: :replace, undef: :replace, replace: "\uFFFD").bytes
end

def present_hash(value, source)
  return nil if value.nil?

  { "value" => value, "source" => source }
end

def find_token_id(token_value, config, generation_config, tokenizer)
  token_value = token_content(token_value)
  ids = []
  ids << config["bos_token_id"] if token_value == token_content(config["bos_token"])
  ids << config["eos_token_id"] if token_value == token_content(config["eos_token"])
  ids << config["pad_token_id"] if token_value == token_content(config["pad_token"])
  ids << config["unk_token_id"] if token_value == token_content(config["unk_token"])
  ids << generation_config["bos_token_id"] if token_value == token_content(generation_config["bos_token"])
  ids << generation_config["eos_token_id"] if token_value == token_content(generation_config["eos_token"])
  ids << generation_config["pad_token_id"] if token_value == token_content(generation_config["pad_token"])

  Array(tokenizer["added_tokens"]).each do |token|
    next unless token.is_a?(Hash) && token["content"] == token_value

    ids << token["id"]
  end

  decoder = tokenizer["added_tokens_decoder"]
  if decoder.is_a?(Hash)
    decoder.each do |id, token|
      content = token.is_a?(Hash) ? token["content"] : token
      ids << id.to_i if content == token_value
    end
  end

  ids.compact.uniq
end

def token_content(value)
  value.is_a?(Hash) ? value["content"] : value
end

def token_entry(name, value, config, generation_config, tokenizer, placeholder = nil)
  value = token_content(value)
  return nil if value.nil?

  placeholder ||= if value.to_s.include?("im_start") || name == "bos_token"
                    "CHAT_START_TOKEN"
                  elsif value.to_s.include?("im_end") || name == "eos_token"
                    "CHAT_END_TOKEN"
                  end

  {
    "name" => name,
    "placeholder" => placeholder || PLACEHOLDER_NAMES.fetch(name, name.upcase),
    "ids" => find_token_id(value, config, generation_config, tokenizer),
    "bytes" => byte_array(value),
    "escaped" => safe_string(value)
  }
end

def label_chat_template(template)
  return nil unless template

  safe = safe_string(template)
  structure = []
  structure << "contains system role handling" if template.include?("system")
  structure << "contains user role handling" if template.include?("user")
  structure << "contains assistant role handling" if template.include?("assistant")
  structure << "contains generation prompt branch" if template.include?("add_generation_prompt")
  structure << "contains loop over messages" if template.include?("messages")
  structure << "requires manual chat template construction unless tokenizer runtime applies it" if structure.empty?

  {
    "structure" => structure,
    "safe_preview" => safe[0, 500],
    "assistant_prefix" => template.include?("assistant") ? "ASSISTANT_GENERATION_PREFIX" : nil,
    "role_handling" => {
      "system" => template.include?("system"),
      "user" => template.include?("user"),
      "assistant" => template.include?("assistant")
    }
  }
end

def discover_external_data(model_dir, onnx_file)
  present = Dir.glob(File.join(model_dir, "**", "*.onnx_data")).sort
  missing = []

  if onnx_file && File.file?(onnx_file)
    content = File.binread(onnx_file, 2 * 1024 * 1024)
    content.scan(/[A-Za-z0-9_.-]+\.onnx_data/).uniq.each do |name|
      candidate = File.join(File.dirname(onnx_file), name)
      missing << name unless File.exist?(candidate)
    end
  end

  [present, missing]
end

def onnx_metadata(onnx_file)
  return [{ "available" => false, "reason" => "no ONNX file discovered" }, nil, nil] unless onnx_file

  begin
    require "onnxruntime"
  rescue LoadError
    return [{ "available" => false, "reason" => "onnxruntime gem is not available" }, [], []]
  end

  model = OnnxRuntime::Model.new(onnx_file)
  inputs = Array(model.inputs).each_with_index.map { |input, index| tensor_metadata(input, "input_#{index}") }
  outputs = Array(model.outputs).each_with_index.map { |output, index| tensor_metadata(output, "output_#{index}") }
  [{ "available" => true, "source" => "onnx_metadata" }, inputs, outputs]
rescue StandardError => e
  [{ "available" => false, "reason" => safe_string("#{e.class}: #{e.message}") }, [], []]
end

def tensor_metadata(tensor, fallback_name)
  fetcher = tensor.respond_to?(:fetch)
  {
    "name" => fetcher ? tensor.fetch("name", tensor.fetch(:name, fallback_name)) : fallback_name,
    "type" => fetcher ? tensor.fetch("type", tensor.fetch(:type, nil)) : nil,
    "shape" => fetcher ? tensor.fetch("shape", tensor.fetch(:shape, nil)) : nil,
    "source" => "onnx_metadata"
  }
end

def cache_contract(config, inputs, outputs)
  layer_count = config["num_hidden_layers"]
  kv_heads = config["num_key_value_heads"] || config["num_attention_heads"]
  head_dim = config["head_dim"] || (config["hidden_size"].to_i / config["num_attention_heads"].to_i if config["hidden_size"] && config["num_attention_heads"].to_i.positive?)
  cache_inputs = Array(inputs).select { |input| input["name"].to_s.include?("past_key_values") || input["name"].to_s.start_with?("past.") }
  cache_outputs = Array(outputs).select { |output| output["name"].to_s.include?("present") }

  mapping = cache_outputs.map do |output|
    {
      "present" => output["name"],
      "past_key_values" => output["name"].to_s.sub(/^present/, "past_key_values"),
      "source" => "name_pattern"
    }
  end

  {
    "first_pass_empty_cache_required" => {
      "value" => cache_inputs.any? ? true : nil,
      "source" => cache_inputs.any? ? "onnx_metadata" : "metadata_gap"
    },
    "cache_layer_count" => present_hash(layer_count, "inferred_from_config"),
    "kv_heads" => present_hash(kv_heads, kv_heads == config["num_key_value_heads"] ? "inferred_from_config" : "fallback_attention_heads"),
    "head_dimension" => present_hash(head_dim, config["head_dim"] ? "inferred_from_config" : "derived_from_hidden_size"),
    "empty_cache_shape" => {
      "value" => layer_count && kv_heads && head_dim ? [1, kv_heads, 0, head_dim] : nil,
      "source" => layer_count && kv_heads && head_dim ? "inferred_from_config" : "metadata_gap"
    },
    "present_to_past_mapping" => mapping
  }
end

def runtime_probe(onnx_file, timeout_seconds)
  return { "enabled" => false, "source" => "disabled" } unless onnx_file

  begin
    Timeout.timeout(timeout_seconds) do
      begin
        require "onnxruntime"
      rescue LoadError
        return { "enabled" => true, "source" => "runtime_probe", "status" => "skipped", "reason" => "onnxruntime gem is not available" }
      end

      model = OnnxRuntime::Model.new(onnx_file)
      {
        "enabled" => true,
        "source" => "runtime_probe",
        "status" => "metadata_only",
        "input_count" => Array(model.inputs).length,
        "output_count" => Array(model.outputs).length,
        "bounded_forward_passes" => 0,
        "notes" => [
          "full forward probing requires artifact-specific tensor allocation and remains bounded to at most two passes"
        ]
      }
    end
  rescue Timeout::Error
    { "enabled" => true, "source" => "runtime_probe", "status" => "failed", "reason" => "probe timed out after #{timeout_seconds} seconds" }
  rescue StandardError => e
    { "enabled" => true, "source" => "runtime_probe", "status" => "failed", "reason" => safe_string("#{e.class}: #{e.message}") }
  end
end

def table(rows)
  return "_None._\n" if rows.empty?

  header = rows.first.keys
  lines = []
  lines << "| #{header.join(" | ")} |"
  lines << "| #{header.map { "---" }.join(" | ")} |"
  rows.each do |row|
    lines << "| #{header.map { |key| row[key].nil? || row[key] == "" ? "-" : row[key] }.join(" | ")} |"
  end
  "#{lines.join("\n")}\n"
end

def markdown(report)
  files = report.fetch("files")
  token_data = report.fetch("tokenizer_and_chat_template")
  onnx = report.fetch("onnx_contract")
  kv = report.fetch("kv_cache_and_incremental_generation")
  probe = report.fetch("runtime_probe_results")

  token_rows = token_data.fetch("special_tokens").map do |token|
    {
      "Name" => token["name"],
      "Placeholder" => token["placeholder"],
      "IDs" => token["ids"].join(", "),
      "Bytes" => token["bytes"].inspect
    }
  end

  input_rows = Array(onnx["inputs"]).map { |item| { "Name" => item["name"], "Type" => item["type"].inspect, "Shape" => item["shape"].inspect, "Source" => item["source"] } }
  output_rows = Array(onnx["outputs"]).map { |item| { "Name" => item["name"], "Type" => item["type"].inspect, "Shape" => item["shape"].inspect, "Source" => item["source"] } }
  risks = report.fetch("risks")

  <<~MARKDOWN
    ## Safe Model Artifact Contract

    Model directory: `#{safe_string(report.fetch("model_dir"))}`

    ### Files

    #{table(files.slice(*CONFIG_FILES.map { |name| name.tr(".", "_") }).map { |name, info| { "File" => name, "Path" => info && info["relative_path"], "Present" => !info.nil? } })}
    - ONNX file: #{files["onnx_file"] ? "`#{safe_string(files["onnx_file"]["relative_path"])}`" : "not found"}
    - External ONNX data files: #{files["external_onnx_data_files"].map { |item| "`#{safe_string(item["relative_path"])}`" }.join(", ").then { |value| value.empty? ? "none found" : value }}
    - Missing external ONNX data files: #{files["missing_external_onnx_data_files"].empty? ? "none detected" : files["missing_external_onnx_data_files"].map { |name| "`#{safe_string(name)}`" }.join(", ")}

    ### Tokenizer And Chat Template

    #{table(token_rows)}
    - Chat template structure: #{Array(token_data.dig("chat_template", "structure")).join("; ")}
    - Assistant prefix: #{token_data.dig("chat_template", "assistant_prefix") || "not detected"}
    - BOS/EOS/PAD/UNK IDs: #{token_data.fetch("token_ids").inspect}

    ### Encoding And Decoding

    - Manual chat template construction: #{report.dig("encoding_and_decoding", "manual_chat_template_construction")}
    - Role labels plain text: #{report.dig("encoding_and_decoding", "role_labels_plain_text")}
    - Decode guidance: #{report.dig("encoding_and_decoding", "decode_guidance")}
    - Stop token IDs: #{Array(report.dig("encoding_and_decoding", "stop_token_ids")).inspect}
    - Special-token stripping risk: #{report.dig("encoding_and_decoding", "special_token_stripping_risk")}

    ### ONNX Contract

    - Metadata: #{onnx.dig("metadata", "available") ? "available" : "unavailable"}#{onnx.dig("metadata", "reason") ? " (#{onnx.dig("metadata", "reason")})" : ""}

    Inputs:

    #{table(input_rows)}
    Outputs:

    #{table(output_rows)}
    ### KV Cache And Incremental Generation

    - First-pass empty cache requirement: #{kv.dig("first_pass_empty_cache_required", "value").inspect} (#{kv.dig("first_pass_empty_cache_required", "source")})
    - Cache layer count: #{kv.dig("cache_layer_count", "value").inspect} (#{kv.dig("cache_layer_count", "source")})
    - KV heads: #{kv.dig("kv_heads", "value").inspect} (#{kv.dig("kv_heads", "source")})
    - Head dimension: #{kv.dig("head_dimension", "value").inspect} (#{kv.dig("head_dimension", "source")})
    - Empty cache shape: #{kv.dig("empty_cache_shape", "value").inspect} (#{kv.dig("empty_cache_shape", "source")})
    - Present-to-past mappings: #{kv.fetch("present_to_past_mapping").length}

    ### Runtime Probe Results

    - Status: #{probe["status"] || (probe["enabled"] ? "not run" : "disabled")}
    - Source: #{probe["source"]}
    - Logits shape: #{probe["logits_shape"].inspect}
    - Next-token slice: #{probe["next_token_slice"].inspect}
    - Attention mask behavior: #{probe["attention_mask_shape_behavior"].inspect}
    - Position ID behavior: #{probe["position_id_behavior"].inspect}

    ### Risks

    #{risks.empty? ? "- none detected\n" : risks.map { |risk| "- #{risk["severity"]}: #{risk["message"]}" }.join("\n")}
  MARKDOWN
end

files = {}
json_by_name = {}
CONFIG_FILES.each do |name|
  path = File.join(model_dir, name)
  key = name.tr(".", "_")
  if File.file?(path)
    files[key] = { "relative_path" => name, "bytes" => File.size(path) }
    json_by_name[name] = read_json(path) || {}
  else
    files[key] = nil
    json_by_name[name] = {}
  end
end

unless CONFIG_FILES.any? { |name| File.file?(File.join(model_dir, name)) }
  abort "no tokenizer/config files found in #{model_dir}"
end

config = json_by_name.fetch("config.json")
generation_config = json_by_name.fetch("generation_config.json")
tokenizer_config = json_by_name.fetch("tokenizer_config.json")
special_tokens = json_by_name.fetch("special_tokens_map.json")
tokenizer = json_by_name.fetch("tokenizer.json")

onnx_file = Dir.glob(File.join(model_dir, "**", "*.onnx")).sort.first
external_data, missing_external_data = discover_external_data(model_dir, onnx_file)
files["onnx_file"] = onnx_file ? { "relative_path" => relative_path(model_dir, onnx_file), "bytes" => File.size(onnx_file) } : nil
files["external_onnx_data_files"] = external_data.map { |path| { "relative_path" => relative_path(model_dir, path), "bytes" => File.size(path) } }
files["missing_external_onnx_data_files"] = missing_external_data

risks = []
CONFIG_FILES.each do |name|
  key = name.tr(".", "_")
  risks << { "severity" => "warning", "message" => "#{name} was not found" } if files[key].nil?
  parse_error = json_by_name.dig(name, "__parse_error__")
  risks << { "severity" => "error", "message" => "#{name} could not be parsed: #{safe_string(parse_error)}" } if parse_error
end
risks << { "severity" => "warning", "message" => "no ONNX file was discovered" } unless onnx_file
missing_external_data.each do |name|
  risks << { "severity" => "error", "message" => "referenced external ONNX data file is missing: #{safe_string(name)}" }
end

metadata, inputs, outputs = onnx_metadata(onnx_file)
probe = options[:probes] ? runtime_probe(onnx_file, options[:probe_timeout]) : { "enabled" => false, "source" => "disabled" }
risks << { "severity" => "warning", "message" => "ONNX metadata unavailable: #{metadata["reason"]}" } if metadata && metadata["available"] == false && onnx_file
risks << { "severity" => "warning", "message" => "runtime probe failed: #{probe["reason"]}" } if probe["status"] == "failed"

token_values = []
%w[bos_token eos_token pad_token unk_token].each do |name|
  value = special_tokens[name] || tokenizer_config[name] || config[name]
  token_values << token_entry(name, value, config, generation_config, tokenizer)
end

Array(tokenizer["added_tokens"]).each do |token|
  next unless token.is_a?(Hash)

  token_values << {
    "name" => "added_token",
    "placeholder" => if token["content"].to_s.include?("im_start")
                       "CHAT_START_TOKEN"
                     elsif token["content"].to_s.include?("im_end")
                       "CHAT_END_TOKEN"
                     elsif token["special"]
                       "SPECIAL_ADDED_TOKEN_#{token["id"]}"
                     else
                       "ADDED_TOKEN_#{token["id"]}"
                     end,
    "ids" => [token["id"]].compact,
    "bytes" => byte_array(token["content"]),
    "escaped" => safe_string(token["content"]),
    "special" => token["special"]
  }
end

token_values = token_values.compact.uniq { |entry| [entry["placeholder"], entry["ids"], entry["bytes"]] }
token_ids = {
  "bos_token_id" => config["bos_token_id"] || generation_config["bos_token_id"],
  "eos_token_id" => config["eos_token_id"] || generation_config["eos_token_id"],
  "pad_token_id" => config["pad_token_id"] || generation_config["pad_token_id"],
  "unk_token_id" => config["unk_token_id"] || generation_config["unk_token_id"]
}

stop_token_ids = Array(generation_config["eos_token_id"] || config["eos_token_id"]).compact
chat_template = tokenizer_config["chat_template"]

report = {
  "model_dir" => model_dir,
  "files" => files,
  "tokenizer_and_chat_template" => {
    "chat_template" => label_chat_template(chat_template),
    "special_tokens" => token_values,
    "token_ids" => token_ids,
    "model_type" => present_hash(config["model_type"], "config.json"),
    "architectures" => present_hash(config["architectures"], "config.json"),
    "context_length" => present_hash(tokenizer_config["model_max_length"] || config["max_position_embeddings"], tokenizer_config["model_max_length"] ? "tokenizer_config.json" : "config.json"),
    "vocab_size" => present_hash(config["vocab_size"], "config.json")
  },
  "encoding_and_decoding" => {
    "manual_chat_template_construction" => chat_template ? "required when runtime tokenizer cannot apply chat templates" : "unknown; no chat template discovered",
    "role_labels_plain_text" => chat_template ? %w[system user assistant].select { |role| chat_template.include?(role) } : [],
    "decode_guidance" => "decode generated token IDs after the prompt span; strip only verified special token IDs, not arbitrary text",
    "stop_token_ids" => stop_token_ids,
    "special_token_stripping_risk" => "high if decoding removes all special-like text before verifying stop token IDs"
  },
  "onnx_contract" => {
    "metadata" => metadata,
    "inputs" => inputs,
    "outputs" => outputs,
    "input_count" => Array(inputs).length,
    "output_count" => Array(outputs).length
  },
  "kv_cache_and_incremental_generation" => cache_contract(config, inputs, outputs),
  "runtime_probe_results" => probe,
  "risks" => risks
}

case options[:format]
when "json"
  puts JSON.pretty_generate(report)
when "markdown"
  puts markdown(report)
when "both"
  puts markdown(report)
  puts
  puts "```json"
  puts JSON.pretty_generate(report)
  puts "```"
end
