#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

DEFAULT_KEYS = %w[
  architectures
  model_type
  use_cache
  num_hidden_layers
  num_key_value_heads
  num_attention_heads
  head_dim
  hidden_size
  vocab_size
  model_max_length
  max_position_embeddings
  bos_token_id
  eos_token_id
  pad_token_id
  bos_token
  eos_token
  pad_token
  unk_token
  chat_template
].freeze

def safe(value)
  return "nil" if value.nil?

  text = value.to_s.encode("UTF-8", invalid: :replace, undef: :replace, replace: "\uFFFD").dump[1...-1]
  text
    .gsub("<", "\\x3c")
    .gsub(">", "\\x3e")
    .gsub("|", "\\x7c")
    .gsub("{", "\\x7b")
    .gsub("}", "\\x7d")
end

path = ARGV.shift
keys = ARGV.empty? ? DEFAULT_KEYS : ARGV

abort "usage: ruby scripts/safe_model_json.rb PATH [KEY ...]" unless path

data = JSON.parse(File.read(path))

keys.each do |key|
  next unless data.key?(key)

  suffix = key.end_with?("_token", "chat_template") ? "_safe" : ""
  puts "#{key}#{suffix}: #{safe(data[key])}"
end

decoder = data["added_tokens_decoder"]
if decoder.is_a?(Hash)
  decoder.each do |token_id, token|
    content = token.is_a?(Hash) ? token["content"] : token
    special = token.is_a?(Hash) ? token["special"] : nil
    puts "added_token: id=#{safe(token_id)} special=#{safe(special)} content_safe=#{safe(content)}"
  end
end
