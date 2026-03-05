# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Obsidian vault for personal knowledge management and daily memos. iCloud sync enabled.

## Directory Structure

- `anote/01-Templete/` - Templates (`DailyMemoTemplete.md`, `Templete.md`, `構造化面接Templete.md`)
- `anote/02-DailyMemo/` - Daily journal entries (`YYYY-MM-DD.md` format, optional `【イベント名】` suffix)
- `anote/03-input/` - Input/reference materials organized by type:
  - `book/` - Book summaries and reading notes (includes `読了リスト.md`)
  - `interview/` - Interview notes and structured interview templates
  - `article/`, `information/`, `memory/`, `youtube/`, `面接対策/`
- `anote/04-output/` - Generated content and outputs
- `anote/05-anno/` - Personal content

## Obsidian Plugins

- **Templater** - Template management with dynamic content
- **Dataview** - Note querying and data display
- **Typing Assistant** - Enhanced typing

## File Conventions

- YAML frontmatter with `created`, `tags` fields
- Japanese language is primary
- Daily memos follow the template structure: TODO, 今週優先すること, 今日優先すること, 小さな成功, 今日やったこと, 自己省察, 学んだこと, 明日すること, 明日へのアクション, Memo

## Tag Management Rules

From `.cursor/rules/globals.mdc` - these rules must be followed when creating or modifying tags:

- **Lowercase only**: All tags in lowercase
- **No spaces**: Use hyphens (`-`) or underscores (`_`) as separators
- **Singular form**: Use `#note` not `#notes`
- **Content tags only**: Tags describe the topic/subject matter. Prohibited: status tags (`#未整理`), time tags (`#2023`), location tags (`#東京`)
- **No special characters or emoji** in tag names
- **Max 5 tags per note**
- **Check existing tags** before creating new ones to avoid duplicates
- **Prohibited tags**: `TODO`, `ROUTINE`, `JOURNAL`, `STUDY`, `EXERCISE` (these are daily activities, not topics)
- **Use official names** for proper nouns; only well-known abbreviations allowed (`#ai`, `#ui`)

## Important Considerations

- This is a personal knowledge management system, not a code repository
- Respect existing organizational structure when creating or modifying files
- Files sync via iCloud - avoid operations that might conflict with sync
