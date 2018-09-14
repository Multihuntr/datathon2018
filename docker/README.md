# What the mess?

The postgresql configuration file has one line changed. The one that makes it open to connections from everywhere.

The db.Dockerfile appends a line that allows connections from anywhere to the database. Why do we need both? Gosh I wish I knew.