# {{ORG_NAME}} Story Agent Configuration
# Copy this file to .env and fill in your values
# DO NOT commit .env to version control

# ===========================================
# JIRA / Atlassian Configuration
# ===========================================

# Your Atlassian site URL
# Format: https://your-domain.atlassian.net
ATLASSIAN_SITE_URL=https://your-domain.atlassian.net

# Your Atlassian account email
ATLASSIAN_USER_EMAIL=your-email@company.com

# API Token for authentication
# Generate at: https://id.atlassian.com/manage-profile/security/api-tokens
ATLASSIAN_API_TOKEN=your-api-token-here

# Default JIRA project key for story creation
JIRA_DEFAULT_PROJECT={{JIRA_PROJECT}}

# ===========================================
# Optional Configuration
# ===========================================

# Default story output directory (relative to project root)
STORY_OUTPUT_DIR=./stories

# Enable debug logging (true/false)
DEBUG=false

# Default Epic link for new stories (optional)
# JIRA_DEFAULT_EPIC=PROJ-100
