import pandas as pd
file_path=r"C:\Users\Verukonda Supriya\OneDrive\Desktop\quiz_project\python_quiz_questions.csv"
def get_random_questions_from_csv(file_path, num_questions=30):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Check if there are enough questions in the dataset
    if len(df) < num_questions:
        num_questions = len(df)

    # Randomly select the specified number of questions
    random_questions = df.sample(n=num_questions).to_dict(orient='records')

    return random_questions
