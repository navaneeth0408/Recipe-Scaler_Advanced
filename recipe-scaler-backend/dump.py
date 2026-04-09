import traceback
try:
    import app.routes.ai
except Exception as e:
    with open('error_dump.txt', 'w') as f:
        traceback.print_exc(file=f)
