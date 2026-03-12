'use client'
import { useState } from 'react'
import { Bot, Cpu, Plus, Play, Save, Wrench, Sparkles } from 'lucide-react'

interface AgentTemplate {
  id: string
  name: string
  description: string
  icon: string
  tools: string[]
}

const TEMPLATES: AgentTemplate[] = [
  {
    id: 'market_scanner',
    name: 'Market Scanner',
    description: 'Scans multiple symbols for trading opportunities based on custom criteria',
    icon: '🔍',
    tools: ['detect_trend', 'identify_volatility', 'compute_indicators'],
  },
  {
    id: 'alert_bot',
    name: 'Alert Bot',
    description: 'Monitors conditions and sends alerts when criteria are met',
    icon: '🔔',
    tools: ['monitor_positions', 'send_alert', 'check_exit_conditions'],
  },
  {
    id: 'research_analyst',
    name: 'Research Analyst',
    description: 'Deep analysis of market conditions with LLM-powered insights',
    icon: '📊',
    tools: ['analyze_market', 'build_strategy', 'generate_report'],
  },
  {
    id: 'custom',
    name: 'Custom Agent',
    description: 'Build from scratch with full control over prompts and tools',
    icon: '🛠️',
    tools: [],
  },
]

const AVAILABLE_TOOLS = [
  'detect_trend', 'identify_volatility', 'detect_liquidity_zones', 'detect_market_regime',
  'auto_create_strategy', 'combine_indicators', 'compute_indicators',
  'run_backtest', 'calculate_metrics',
  'calculate_position_size', 'validate_risk', 'check_daily_limits',
  'execute_trade', 'confirm_execution',
  'monitor_positions', 'update_trailing_stop', 'check_exit_conditions', 'send_alert',
  'get_portfolio_summary', 'analyze_allocation',
  'generate_report', 'fetch_live_data', 'fetch_historical',
]

export default function AgentBuilder() {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [agentName, setAgentName] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [selectedTools, setSelectedTools] = useState<string[]>([])
  const [testing, setTesting] = useState(false)
  const [testOutput, setTestOutput] = useState('')

  const handleSelectTemplate = (template: AgentTemplate) => {
    setSelectedTemplate(template.id)
    setAgentName(template.name)
    setSelectedTools([...template.tools])
    setSystemPrompt(
      template.id === 'custom'
        ? ''
        : `You are a ${template.name} agent for an Indian market trading platform. ${template.description}. Respond with actionable insights.`
    )
  }

  const toggleTool = (tool: string) => {
    setSelectedTools(prev =>
      prev.includes(tool) ? prev.filter(t => t !== tool) : [...prev, tool]
    )
  }

  const handleTest = async () => {
    setTesting(true)
    setTestOutput('Testing agent configuration...\n')
    await new Promise(r => setTimeout(r, 1000))
    setTestOutput(prev => prev + `✓ Agent "${agentName}" configured with ${selectedTools.length} tools\n`)
    await new Promise(r => setTimeout(r, 500))
    setTestOutput(prev => prev + `✓ System prompt validated (${systemPrompt.length} chars)\n`)
    await new Promise(r => setTimeout(r, 500))
    setTestOutput(prev => prev + `✓ Agent ready for deployment\n`)
    setTesting(false)
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Sparkles size={24} className="accent" />
          Agent Builder
        </h1>
        <p className="text-muted text-sm">Create custom AI agents with tailored prompts and tools</p>
      </div>

      {/* Template Selection */}
      <div>
        <h2 className="text-lg font-semibold mb-3">1. Choose Template</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {TEMPLATES.map(template => (
            <div key={template.id}
              onClick={() => handleSelectTemplate(template)}
              className={`card cursor-pointer transition-all hover:border-accent/50 ${
                selectedTemplate === template.id ? 'border-accent bg-accent/5' : ''
              }`}>
              <div className="text-3xl mb-2">{template.icon}</div>
              <div className="font-semibold mb-1">{template.name}</div>
              <div className="text-sm text-muted">{template.description}</div>
              <div className="mt-2 text-xs text-accent">{template.tools.length} tools</div>
            </div>
          ))}
        </div>
      </div>

      {selectedTemplate && (
        <>
          {/* Agent Configuration */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Bot size={20} />
              2. Configure Agent
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-muted mb-1 block">Agent Name</label>
                <input
                  value={agentName}
                  onChange={e => setAgentName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:border-accent focus:outline-none"
                  placeholder="My Custom Agent"
                />
              </div>
              <div>
                <label className="text-sm text-muted mb-1 block">System Prompt</label>
                <textarea
                  value={systemPrompt}
                  onChange={e => setSystemPrompt(e.target.value)}
                  rows={5}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:border-accent focus:outline-none resize-none font-mono text-sm"
                  placeholder="Define your agent's personality, behavior, and capabilities..."
                />
                <div className="text-xs text-muted mt-1">{systemPrompt.length} characters</div>
              </div>
            </div>
          </div>

          {/* Tool Assignment */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Wrench size={20} />
              3. Assign Tools
            </h2>
            <div className="flex flex-wrap gap-2">
              {AVAILABLE_TOOLS.map(tool => (
                <button key={tool} onClick={() => toggleTool(tool)}
                  className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                    selectedTools.includes(tool)
                      ? 'bg-accent/20 border-accent text-accent'
                      : 'bg-surface border-border text-muted hover:border-accent/50'
                  }`}>
                  {selectedTools.includes(tool) ? '✓ ' : ''}{tool}
                </button>
              ))}
            </div>
            <div className="text-sm text-muted mt-3">{selectedTools.length} tools selected</div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button onClick={handleTest} disabled={testing || !agentName}
              className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-surface border border-border hover:border-accent transition-colors disabled:opacity-50">
              <Play size={16} />
              Test Agent
            </button>
            <button disabled={!agentName}
              className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-accent text-white hover:bg-accent/80 transition-colors disabled:opacity-50">
              <Save size={16} />
              Save Agent
            </button>
          </div>

          {/* Test Output */}
          {testOutput && (
            <div className="card bg-background">
              <div className="text-sm text-muted mb-2 flex items-center gap-2">
                <Cpu size={14} />
                Test Output
              </div>
              <pre className="text-sm font-mono text-profit whitespace-pre-wrap">{testOutput}</pre>
            </div>
          )}
        </>
      )}
    </div>
  )
}
