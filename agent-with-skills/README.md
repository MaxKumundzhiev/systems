# Reference
[The-Complete-Guide-to-Building-Skill-for-Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

# Intro
Skiils are set of rules, preferences and things which might be handy for agent.
Instaed of repeatable explanations you might refer to a particular skill.

Skills are handy for repeatable workflows: generating frontend
designs from specs, conducting research with consistent methodology, creating
documents that follow your team's style guide, or orchestrating multi-step
processes.


# Fundamentals
A skill is a folder containing:
1. SKILL.md     - (required): Instructions in Markdown with YAML frontmatter
2. scripts/     - (optional): Executable code (Python, Bash, etc.) 
3. references/  - (optional): Documentation loaded as needed
4. assets/      - (optional): Templates, fonts, icons used in output


# Notes
`Before writing any code, identify 2-3 concrete use cases your skill should enable.`
```text
Use Case: Project Sprint Planning
Trigger: User says "help me plan this sprint" or "create sprint tasks"
Steps:
    1. Fetch current project status from Linear (via MCP)
    2. Analyze team velocity and capacity
    3. Suggest task prioritization
    4. Create tasks in Linear with proper labels and estimates
Result: Fully planned sprint with tasks created

Ask yourself:
• What does a user want to accomplish?
• What multi-step workflows does this require?
• Which tools are needed (built-in or MCP?)
• What domain knowledge or best practices should be embedded?
```

`Define success criteria`
```
How will you know your skill is working?
These are aspirational targets - rough benchmarks rather than precise
thresholds. Aim for rigor but accept that there will be an element of vibes-based
assessment. We are actively developing more robust measurement guidance and
tooling.

Quantitative metrics:
• Skill triggers on 90% of relevant queries
– How to measure: Run 10-20 test queries that should trigger your skill. Track how many times it loads automatically vs. requires explicit invocation.

• Completes workflow in X tool calls
– How to measure: Compare the same task with and without the skill enabled. Count tool calls and total tokens consumed.

• 0 failed API calls per workflow
– How to measure: Monitor MCP server logs during test runs. Track retry rates and error codes.

Qualitative metrics:
• Users don't need to prompt Claude about next steps
– How to assess: During testing, note how often you need to redirect or clarify. Ask beta users for feedback.

• Workflows complete without user correction
– How to assess: Run the same request 3-5 times. Compare outputs for structural consistency and quality.

• Consistent results across sessions
– How to assess: Can a new user accomplish the task on first try with minimal guidance?
```

`Skill folder structure`
```text
File structure
your-skill-name/
    ├── SKILL.md # Required - main skill file
    ├── scripts/ # Optional - executable code
    │ ├── process_data.py # Example
    │ └── validate.sh # Example
    ├── references/ # Optional - documentation
    │ ├── api-guide.md # Example
    │ └── examples/ # Example
    └── assets/ # Optional - templates, etc.
    └── report-template.md # Example
```

`SKILL.md file structure`
```
This is called !!!frontmatter!!!
---
name: your-skill
description: [...]
---

# Your Skill Name

# Instructions
### Step 1: [First Major Step]
Clear explanation of what happens.
```

`Writing effective skills`
The YAML frontmatter: The most important part in SKILL.md, becuase The YAML frontmatter is how Claude decides whether to load your skill
```
!!! The description should be formed as: [What it does] + [When to use it] + [Key capabilities] !!!
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

`Examples of good descriptions:`
```
# Good - specific and actionable
description: Analyzes Figma design files and generates
developer handoff documentation. Use when user uploads .fig
files, asks for "design specs", "component documentation", or
"design-to-code handoff".

# Good - includes trigger phrases
description: Manages Linear project workflows including sprint
planning, task creation, and status tracking. Use when user
mentions "sprint", "Linear tasks", "project planning", or asks
to "create tickets".

# Good - clear value proposition
description: End-to-end customer onboarding workflow for
PayFlow. Handles account creation, payment setup, and
subscription management. Use when user says "onboard new
customer", "set up subscription", or "create PayFlow account".
```

`Examples of bad descriptions:`
```
# Too vague
description: Helps with projects.

# Missing triggers
description: Creates sophisticated multi-page documentation
systems.

# Too technical, no user triggers
description: Implements the Project entity model with
hierarchical relationships.
```