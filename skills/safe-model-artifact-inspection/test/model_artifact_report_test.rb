# frozen_string_literal: true

require "json"
require "minitest/autorun"
require "open3"
require "tmpdir"

class ModelArtifactReportTest < Minitest::Test
  SCRIPT = File.expand_path("../scripts/model_artifact_report.rb", __dir__)
  SKILL_DOC = File.expand_path("../SKILL.md", __dir__)

  def run_report(model_dir, *args)
    Open3.capture3("ruby", SCRIPT, model_dir, *args)
  end

  def write_json(dir, name, payload)
    File.write(File.join(dir, name), JSON.pretty_generate(payload))
  end

  def write_basic_model(dir)
    start_token = [60, 124, 105, 109, 95, 115, 116, 97, 114, 116, 124, 62].pack("C*")
    end_token = [60, 124, 105, 109, 95, 101, 110, 100, 124, 62].pack("C*")

    write_json(dir, "config.json", {
      "architectures" => ["SmolLMForCausalLM"],
      "model_type" => "smollm",
      "num_hidden_layers" => 2,
      "num_key_value_heads" => 3,
      "num_attention_heads" => 6,
      "head_dim" => 8,
      "hidden_size" => 48,
      "vocab_size" => 1000,
      "max_position_embeddings" => 2048,
      "bos_token_id" => 1,
      "eos_token_id" => 2,
      "pad_token_id" => 2,
      "use_cache" => true
    })
    write_json(dir, "generation_config.json", {
      "eos_token_id" => [2, 7],
      "pad_token_id" => 2,
      "max_new_tokens" => 64
    })
    write_json(dir, "tokenizer_config.json", {
      "model_max_length" => 2048,
      "bos_token" => start_token,
      "eos_token" => end_token,
      "pad_token" => end_token,
      "chat_template" => "#{start_token}system\nx#{end_token}\n#{start_token}assistant\n"
    })
    write_json(dir, "special_tokens_map.json", {
      "bos_token" => start_token,
      "eos_token" => end_token,
      "pad_token" => end_token,
      "unk_token" => "<unk>"
    })
    write_json(dir, "tokenizer.json", {
      "added_tokens" => [
        { "id" => 1, "content" => start_token, "special" => true },
        { "id" => 2, "content" => end_token, "special" => true }
      ],
      "added_tokens_decoder" => {
        "1" => { "content" => start_token, "special" => true },
        "2" => { "content" => end_token, "special" => true }
      }
    })
  end

  def test_reports_markdown_and_json_without_raw_control_delimiters
    Dir.mktmpdir do |dir|
      write_basic_model(dir)
      File.write(File.join(dir, "model.onnx"), "not a real onnx")
      File.write(File.join(dir, "model.onnx_data"), "external weights")

      stdout, stderr, status = run_report(dir, "--format", "both", "--no-probes")

      assert status.success?, stderr
      assert_includes stdout, "## Safe Model Artifact Contract"
      assert_includes stdout, "```json"
      assert_includes stdout, "CHAT_START_TOKEN"
      assert_includes stdout, "[60, 124, 105"
      refute_includes stdout, [60, 124, 105, 109, 95, 115, 116, 97, 114, 116, 124, 62].pack("C*")
      refute_includes stdout, [60, 124, 105, 109, 95, 101, 110, 100, 124, 62].pack("C*")

      json = JSON.parse(stdout.split("```json", 2).last.split("```", 2).first)
      assert_equal dir, json.fetch("model_dir")
      assert_equal "model.onnx", json.dig("files", "onnx_file", "relative_path")
      assert_equal 1, json.dig("files", "external_onnx_data_files").length
      assert_equal 2, json.dig("kv_cache_and_incremental_generation", "cache_layer_count", "value")
      assert_equal "inferred_from_config", json.dig("kv_cache_and_incremental_generation", "cache_layer_count", "source")
    end
  end

  def test_missing_tokenizer_config_is_reported_as_a_risk
    Dir.mktmpdir do |dir|
      write_json(dir, "config.json", { "model_type" => "qwen", "num_hidden_layers" => 1 })

      stdout, stderr, status = run_report(dir, "--format", "json", "--no-probes")

      assert status.success?, stderr
      json = JSON.parse(stdout)
      assert_nil json.dig("files", "tokenizer_config_json")
      assert_includes json.fetch("risks").map { |risk| risk.fetch("message") }, "tokenizer_config.json was not found"
    end
  end

  def test_missing_onnx_file_is_reported_as_a_risk
    Dir.mktmpdir do |dir|
      write_basic_model(dir)

      stdout, stderr, status = run_report(dir, "--format", "json", "--no-probes")

      assert status.success?, stderr
      json = JSON.parse(stdout)
      assert_nil json.dig("files", "onnx_file")
      assert_includes json.fetch("risks").map { |risk| risk.fetch("message") }, "no ONNX file was discovered"
    end
  end

  def test_requires_at_least_one_model_or_tokenizer_config_file
    Dir.mktmpdir do |dir|
      stdout, stderr, status = run_report(dir, "--format", "json", "--no-probes")

      refute status.success?
      assert_empty stdout
      assert_includes stderr, "no tokenizer/config files found"
    end
  end

  def test_marks_missing_external_data_file_from_onnx_reference
    Dir.mktmpdir do |dir|
      write_basic_model(dir)
      File.binwrite(File.join(dir, "model.onnx"), "weights.onnx_data")

      stdout, stderr, status = run_report(dir, "--format", "json", "--no-probes")

      assert status.success?, stderr
      json = JSON.parse(stdout)
      assert_equal ["weights.onnx_data"], json.dig("files", "missing_external_onnx_data_files")
      assert_includes json.fetch("risks").map { |risk| risk.fetch("message") }, "referenced external ONNX data file is missing: weights.onnx_data"
    end
  end

  def test_skill_doc_points_to_report_script_without_python_heredocs
    text = File.read(SKILL_DOC)

    assert_includes text, "model_artifact_report.rb MODEL_DIR --format both"
    refute_match(/python\s+<<|python3\s+<</i, text)
  end
end
