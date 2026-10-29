import os
import sys

# Move to the web app folder and start the server
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "FinED_Bench_unzipped", "fined")

os.chdir(app_dir)
sys.path.insert(0, app_dir)

import app

if __name__ == "__main__":
    app.main()
