#!/usr/bin/env ruby
# Scan RSpec example descriptions for BDD structure-smell keywords.
#
# Usage:
#   ruby skills/verify-specs/scripts/condition_word_audit.rb spec/path/example_spec.rb
#   ruby skills/verify-specs/scripts/condition_word_audit.rb --all

require "optparse"

TRIGGERS = {
  "when" => "condition",
  "with" => "condition",
  "without" => "condition",
  "for" => "condition",
  "and" => "split"
}.freeze

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
  file_hits = []

  File.foreach(filepath, chomp: true).each_with_index do |line, idx|
    match = EXAMPLE_PATTERN.match(line)
    next unless match

    desc = match[:desc]
    words = TRIGGERS.keys.select { |word| desc.match?(/\b#{Regexp.escape(word)}\b/i) }
    next if words.empty?

    display = desc.length > MAX_DESC ? "#{desc[0, MAX_DESC - 3]}..." : desc
    file_hits << {
      line: idx + 1,
      desc: display,
      words: words.sort,
      kinds: words.map { |word| TRIGGERS.fetch(word) }.uniq.sort
    }
  end

  results << [filepath, file_hits] if file_hits.any?
end

results.each do |filepath, hits|
  puts filepath
  hits.each do |hit|
    words = hit[:words].map { |word| %("#{word}") }.join(", ")
    kinds = hit[:kinds].join("/")
    printf("  Line %-4d [?] %-72s  %s: %s\n", hit[:line], hit[:desc], kinds, words)
  end
  puts
end

flagged_count = results.sum { |_filepath, hits| hits.size }
puts "Summary: #{flagged_count} candidate(s) across #{results.size} file(s)"
puts "Note: candidates require reviewer judgment; this does not replace the full verify-specs review."
