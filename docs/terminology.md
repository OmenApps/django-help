# Terminology and Definitions

## App-specific Terms

### Article
An individual help content item, typically containing explanations, instructions, or information on a specific topic.

### Category
A grouping mechanism for organizing articles into related topics or sections.

### Tag
A label or keyword associated with one or more articles, used for classification and easier searching.

### Slug
A URL-friendly version of a text, typically used in web addresses. For example, "how-to-reset-password" might be the slug for an article titled "How to Reset Your Password".

### Intended Entity Type
A classification system used in django-help to specify whether an article or category is intended for a specific type of user or organization (e.g., individual, business, any).

### Relevant Path
A URL path associated with an article, used to provide context-sensitive help based on the user's current location in the application.

### Highlighted Article
An article marked as particularly important or featured, typically given prominence in the user interface.

### Public Article
An article that is visible to all users. Non-public articles may have restricted visibility based on user permissions.

## Multi-language Support

### Translated Field
A field in the database that stores content in multiple languages. In django-help, this is implemented using the django-translated-fields package.

### Language Code
A short string identifying a specific language, typically following the ISO 639-1 standard (e.g., "en" for English, "es" for Spanish).

## Content Management

### Markdown
A lightweight markup language used for formatting text. django-help uses Markdown for writing and storing article content.

### Frontmatter
Metadata at the beginning of a Markdown file, typically written in YAML format. It's used to store additional information about an article, such as its title, tags, and other metadata.

## User Interface

### Modal
A dialog box or popup window that appears on top of the current page. In django-help, modals are used to display article content without navigating away from the current page.

### HTMX
A JavaScript library that allows you to access AJAX, CSS Transitions, WebSockets and Server Sent Events directly in HTML, without writing JavaScript. django-help uses HTMX for dynamic content loading.
