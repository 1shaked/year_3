import ollama
import json as js
from utils_classes import load_and_process_comments
def query_deepseek(prompt):
    # response = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}])
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']


def test_deepseek_model():
    _, _, test_comments, test_labels = load_and_process_comments(
        train_path='train',
        batch_size=50,
    )
    answers = []
    # test current results
    with open('deepseek_answers.json', 'r') as f:
        current_answers = js.load(f)
        len_current = len(current_answers)
    for index, batch in enumerate(test_comments):
        comments ,labels = batch
        for inner_index, comment in enumerate(comments):
            if len_current > 0:
                len_current -= 1
                continue
            answer = query_deepseek(f'''for the following movie review, tell in (0=negative, 1=positive) sentiment:
                {comment}

                answer only with the number (0 or 1) no more text whatsoever''')
            actual_answer = str(labels[inner_index])
            answers.append([answer, actual_answer])
            # save the answer
            with open('deepseek_answers.json', 'w') as f:
                f.write(js.dumps([*current_answers, *answers]))
        print(f"Batch {index} done")
    print(f"Accuracy: {sum(answers) / len(answers)}")


test_deepseek_model()