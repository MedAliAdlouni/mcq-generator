import pytest 
from app.core.llm import generate_mcq

TEXT = """ 
Bees play a crucial role in pollination, which is essential for the reproduction of many plants. 
As they collect nectar, pollen grains stick to their bodies and are transferred from flower to flower. 
This process increases genetic diversity and improves crop yields. Recent studies show that the decline 
in bee populations could significantly impact global food production and ecosystem health. 
Scientists are exploring ways to protect bees through habitat restoration, reduced pesticide use, 
and the promotion of native plant species.
"""

NB_QUESTIONS = 2  

# --------------------------------------------------------------------------------------------------
# Integration (CI) / CD tests
# --------------------------------------------------------------------------------------------------

@pytest.mark.integration
def test_generate_mcq_smoke():
    """ Smoke test:
        - API key
        - Model exists
        - End-to-end call succeeds
    """
    quiz = generate_mcq(text=TEXT, nb_questions=1)

    assert isinstance(quiz, list)
    assert len(quiz) == 1



@pytest.mark.integration
def test_generate_mcq_output_structure():
    """ Contract/ Schema test.
        Test fenerate_mcq function's output structure.
    """
    # Inference
    quiz = generate_mcq(text=TEXT, nb_questions=NB_QUESTIONS)

    assert len(quiz) == 2

    for q in quiz:
        assert "question" in q
        assert "answers" in q
        assert "correct_answer" in q

        assert isinstance(q["answers"], list)
        assert len(q["answers"]) == 4

        # Check if correct_answer matches one of the answers (allowing for minor formatting differences)
        # LLM might return answers with/without trailing periods
        correct_answer_clean = q["correct_answer"].strip().rstrip('.')
        answers_clean = [ans.strip().rstrip('.') for ans in q["answers"]]
        assert correct_answer_clean in answers_clean or q["correct_answer"] in q["answers"]
