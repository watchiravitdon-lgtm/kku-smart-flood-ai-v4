@echo off
python generate_data.py
python train_model.py
streamlit run app.py
pause
