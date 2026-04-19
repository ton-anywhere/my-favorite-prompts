#!/usr/bin/env ruby
# frozen_string_literal: true

require 'yaml'
require 'pathname'

# Skill Registry Utility
#
# Commands:
#   ruby skill_registry.rb list <agent-name>     # List available skills for agent
#   ruby skill_registry.rb check <skill> <agent> # Check if specific skill allowed
#   ruby skill_registry.rb audit                 # Show all restrictions

class SkillRegistry
  REGISTRY_PATH = Pathname(__FILE__).expand_path.join('../registry.yaml')

  def initialize
    @registry = load_registry
  end

  private def load_registry
    YAML.safe_load(File.read(REGISTRY_PATH)) || {}
  rescue Psych::SyntaxError => e
    puts "❌ Error parsing registry: #{e.message}"
    exit 1
  end

  def get_available_skills(agent_name)
    available = []

    @registry.each do |skill_name, config|
      next unless config.is_a?(Hash)

      # Check opt-in restriction first
      if config.key?('granted_agents')
        available << skill_name if config['granted_agents'].include?(agent_name)
        next
      end

      # Check opt-out blocklist
      blocked = Array(config.fetch('blocked_agents', []))
      next if blocked.include?(agent_name)

      # Default: allowed
      available << skill_name
    end

    available.sort
  end

  def is_skill_allowed(skill_name, agent_name)
    return [false, "Skill '#{skill_name}' not found in registry"] unless @registry.key?(skill_name)

    config = @registry[skill_name]

    # Check opt-in restriction
    if config.key?('granted_agents')
      if config['granted_agents'].include?(agent_name)
        [true, 'Granted via explicit allowlist']
      else
        [false, 'Not in granted_agents list']
      end
    else
      # Check blocklist
      blocked = Array(config.fetch('blocked_agents', []))
      if blocked.include?(agent_name)
        reason = config.fetch('reason', 'Blocked by administrator')
        [false, reason]
      else
        [true, 'Allowed by default']
      end
    end
  end

  def show_audit
    puts "\n=== Skill Access Restrictions ===\n"

    restricted_count = 0

    @registry.sort.each do |skill_name, config|
      next unless config.is_a?(Hash)

      description = config.fetch('description', 'No description')

      # Check for granted_agents (opt-in)
      if config.key?('granted_agents')
        restricted_count += 1
        puts "🔒 #{skill_name}"
        puts "   Description: #{description}"
        puts "   Granted to: #{config['granted_agents'].join(', ')}"
        puts
        next
      end

      # Check for blocked_agents (opt-out)
      blocked = Array(config.fetch('blocked_agents', []))
      next unless blocked.any?

      restricted_count += 1
      puts "⚠️  #{skill_name}"
      puts "   Description: #{description}"
      puts "   Blocked from: #{blocked.join(', ')}"
      puts "   Reason: #{config['reason']}" if config.key?('reason')
      puts
    end

    if restricted_count.zero?
      puts 'No restrictions configured. All skills available to all agents.'
    else
      puts "\nTotal restricted skills: #{restricted_count}"
    end
  end

  def list_for_agent(agent_name)
    available = get_available_skills(agent_name)
    all_skills = @registry.keys.select { |k| @registry[k].is_a?(Hash) }
    blocked = (all_skills - available).sort

    puts "\nAvailable skills for '#{agent_name}': (#{available.size})\n"

    available.each do |skill|
      config = @registry[skill] || {}
      desc = config.fetch('description', '')
      truncated = desc.length > 60 ? "#{desc[0..59]}..." : desc
      puts "  ✅ #{skill}"
      puts "     #{truncated}" unless desc.empty?
    end

    return if blocked.empty?

    puts "\nBlocked skills: (#{blocked.size})\n"

    blocked.each do |skill|
      config = @registry[skill]
      reason = config.fetch('reason', 'No reason provided')
      puts "  ❌ #{skill}"
      puts "     #{reason}\n"
    end
  end

  def check_skill(skill_name, agent_name)
    allowed, reason = is_skill_allowed(skill_name, agent_name)

    status = allowed ? '✅ ALLOWED' : '❌ BLOCKED'
    puts "\n#{skill_name} + #{agent_name}: #{status}"
    puts "Reason: #{reason}\n"

    allowed
  end
end

# CLI Handler
class CLIHandler
  def self.run(args)
    registry = SkillRegistry.new

    case args.first
    when 'list'
      handle_list(registry, args)
    when 'check'
      handle_check(registry, args)
    when 'audit'
      handle_audit(registry)
    else
      show_usage
      exit 1
    end
  end

  private_class_method def self.handle_list(registry, args)
    unless args.size == 2
      puts 'Usage: ruby skill_registry.rb list <agent-name>'
      exit 1
    end

    registry.list_for_agent(args[1])
  end

  private_class_method def self.handle_check(registry, args)
    unless args.size == 3
      puts 'Usage: ruby skill_registry.rb check <skill-name> <agent-name>'
      exit 1
    end

    allowed = registry.check_skill(args[1], args[2])
    exit(allowed ? 0 : 1)
  end

  private_class_method def self.handle_audit(registry)
    registry.show_audit
  end

  private_class_method def self.show_usage
    puts <<~USAGE
      Skill Registry Utility

      Commands:
        ruby skill_registry.rb list <agent-name>     # List available skills for agent
        ruby skill_registry.rb check <skill> <agent> # Check if specific skill allowed
        ruby skill_registry.rb audit                 # Show all restrictions
    USAGE
  end
end

# Main entry point
CLIHandler.run(ARGV) if __FILE__ == $PROGRAM_NAME
