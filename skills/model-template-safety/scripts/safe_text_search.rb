#!/usr/bin/env ruby
# frozen_string_literal: true

DEFAULT_TERMS = [
  "chat template",
  "chat_template",
  "special token",
  "special_token",
  "stop token",
  "stop_token",
  "control token",
  "bos",
  "eos",
  "pad",
  "unk",
  "assistant",
  "generation",
  "prompt",
  "tokenizer",
  "past_key_values",
  "present.",
  "position_ids",
  "attention_mask"
].freeze

def safe(value)
  text = value.to_s.encode("UTF-8", invalid: :replace, undef: :replace, replace: "\uFFFD").dump[1...-1]
  text
    .gsub("<", "\\x3c")
    .gsub(">", "\\x3e")
    .gsub("|", "\\x7c")
    .gsub("{", "\\x7b")
    .gsub("}", "\\x7d")
end

path = ARGV.shift
terms = ARGV.empty? ? DEFAULT_TERMS : ARGV.map(&:downcase)

abort "usage: ruby scripts/safe_text_search.rb PATH [TERM ...]" unless path

File.foreach(path, chomp: true).with_index(1) do |line, line_number|
  lower = line.downcase
  next unless terms.any? { |term| lower.include?(term) }

  puts "#{line_number}: #{safe(line)}"
end
