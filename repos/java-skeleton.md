# java-skeleton

## Kind
A project generator written in Node (`bin/cli.js`) that renders Handlebars templates (`.hbs`)
from `templates/`. It is not a Java project: the Java and Gradle code lives in the templates.

## Edit
- Templates under `templates/` (and `templates/manifest.json`).
- `bin/cli.js` only when the change is to the generator itself.
- `DEVLOG.md` (every change), `README.md` (only when usage, commands or flags change),
  `CONTRIBUTING.md` (only when how the repository works changes).

## Do not touch
- Generated projects: they exist only in a temporary directory and are never committed.
- `gradlew` and `gradle-wrapper.jar` in the templates, unless the card is about the wrapper.

## Verify
`CONTRIBUTING.md`, section "How to verify a change": rebuild the image, generate every affected
variant in a temporary directory, build each generated project, and run the app when relevant.

## Skills
None beyond the preloaded ones.

## QA commands
- `docker build`
- `docker run`
- `docker rm`
- `docker image ls`
- `mktemp`
- `id`
- `cd`
- `ls`
- `cat`
- `find`
- `sed -n`
- `node bin/cli.js`
- `./gradlew`
- `java -jar`
- `jar tf`
- `unzip -l`
- `curl`
- `sleep`
- `kill`
- `pkill -f`
