import textstat

def calculate_readability_score(text):
    """
    Calculate the Flesch-Kincaid readability score for the given text.
    
    Args:
        text (str): The text to analyze.
        
    Returns:
        float: A readability score from 0-100, where higher scores indicate easier readability.
    """
    if not text or len(text.strip()) == 0:
        return 0
    
    try:
        # Calculate the Flesch Reading Ease score
        score = textstat.flesch_reading_ease(text)
        
        # Ensure the score is within the 0-100 range
        score = max(0, min(100, score))
        
        return score
    
    except Exception as e:
        print(f"Error calculating readability score: {str(e)}")
        return 0

def get_readability_description(score):
    """
    Get a textual description of what the readability score means.
    
    Args:
        score (float): The Flesch-Kincaid readability score.
        
    Returns:
        tuple: (difficulty_level, education_level, color)
    """
    if score >= 90:
        return ("Very Easy", "5th Grade", "green")
    elif score >= 80:
        return ("Easy", "6th Grade", "green")
    elif score >= 70:
        return ("Fairly Easy", "7th Grade", "green")
    elif score >= 60:
        return ("Standard", "8th & 9th Grade", "yellow")
    elif score >= 50:
        return ("Fairly Difficult", "10th to 12th Grade", "yellow")
    elif score >= 30:
        return ("Difficult", "College", "red")
    else:
        return ("Very Difficult", "College Graduate", "red")
