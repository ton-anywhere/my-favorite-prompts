#!/usr/bin/env ruby
# frozen_string_literal: true

begin
  require "onnxruntime"
rescue LoadError
  abort "onnxruntime gem is not available"
end

path = ARGV.shift
abort "usage: ruby scripts/onnx_metadata.rb PATH_TO_ONNX" unless path

model = OnnxRuntime::Model.new(path)

def field(value, key)
  return nil unless value.respond_to?(:fetch)

  value.fetch(key, nil)
end

puts "INPUTS"
Array(model.inputs).each_with_index do |input, index|
  puts "#{field(input, "name") || "input_#{index}"} type=#{field(input, "type").inspect} shape=#{field(input, "shape").inspect}"
end

puts "OUTPUTS"
Array(model.outputs).each_with_index do |output, index|
  puts "#{field(output, "name") || "output_#{index}"} type=#{field(output, "type").inspect} shape=#{field(output, "shape").inspect}"
end
