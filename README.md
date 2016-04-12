# slack search

this is a really simple flask app for making slack results searchable. 

It uses SQL as a backend, so it should work well for small teams but if you have more than a few hundred K messages its not going to perform well.

To run a debug version locally

```
python init_db.py
python import_db_dump.py slack_export_dir
python search.py
```

To run in production use gunicorn or something like that.