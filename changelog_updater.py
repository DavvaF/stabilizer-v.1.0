
from datetime import datetime

def update_changelog(version, description):
    date = datetime.now().strftime('%Y-%m-%d')
    changelog_entry = f"## Version {version} - {date}\n- {description}\n\n"
    with open("CHANGELOG.md", "a") as f:
        f.write(changelog_entry)
