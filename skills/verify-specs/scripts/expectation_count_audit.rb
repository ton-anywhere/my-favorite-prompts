#!/usr/bin/env ruby
# Scan RSpec examples for multiple expect(...) calls.
#
# Usage:
#   ruby skills/verify-specs/scripts/expectation_count_audit.rb spec/path/example_spec.rb
#   ruby skills/verify-specs/scripts/expectation_count_audit.rb --all

require "optparse"

EXAMPLE_PATTERN = /^\s*(?:it|specify)\s*(?:\.(?:only|skip|pending)\s*)?(?<quote>["'])(?<desc>.*?)(\k<quote>)/
MAX_DESC = 72

options = { all: false }

parser = OptionParser.new do |opts|
  opts.banner = "Usage: ruby #{File.basename($PROGRAM_NAME)} SPEC_FILE [SPEC_FILE ...] | --all"

  opts.on("--all", "Scan spec/**/*_spec.rb from the current project") do
    options[:all] = true
  end

  opts.on("-h", "--help", "Show this help") do
    puts opts
    exit 0
  end
end

parser.parse!(ARGV)

if options[:all] && !ARGV.empty?
  warn "Use either --all or explicit spec file paths, not both."
  exit 2
end

if !options[:all] && ARGV.empty?
  warn parser
  exit 2
end

files = if options[:all]
          Dir.glob("spec/**/*_spec.rb")
        else
          ARGV
        end

missing = files.reject { |path| File.file?(path) }
unless missing.empty?
  warn "Spec file not found: #{missing.join(", ")}"
  exit 2
end

results = []

files.each do |filepath|
  lines = File.readlines(filepath, chomp: true)
  file_hits = []
  current = nil
  block_depth = 0

  lines.each_with_index do |line, idx|
    if current.nil?
      match = EXAMPLE_PATTERN.match(line)
      next unless match

      desc = match[:desc]
      display = desc.length > MAX_DESC ? "#{desc[0, MAX_DESC - 3]}..." : desc
      current = {
        line: idx + 1,
        desc: display,
        expects: 0
      }
      block_depth = 0
    end

    current[:expects] += line.scan(/\bexpect\s*\(/).size
    block_depth += line.scan(/\bdo\b/).size
    block_depth -= line.scan(/^\s*end\s*$/).size

    next unless block_depth <= 0

    file_hits << current if current[:expects] > 1
    current = nil
  end

  results << [filepath, file_hits] if file_hits.any?
end

results.each do |filepath, hits|
  puts filepath
  hits.each do |hit|
    printf("  Line %-4d [?] %-72s  expect calls: %d\n", hit[:line], hit[:desc], hit[:expects])
  end
  puts
end

flagged_count = results.sum { |_filepath, hits| hits.size }
puts "Summary: #{flagged_count} multi-expectation example(s) across #{results.size} file(s)"
puts "Note: candidates require reviewer judgment; this does not replace the full verify-specs review."
