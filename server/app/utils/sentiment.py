def analyze_sentiment(text):
    """Simple sentiment analysis fallback"""
    if not text:
        return 'neutral'
    
    text_lower = text.lower()
    
    # Positive words
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 
        'fantastic', 'wonderful', 'brilliant', 'outstanding', 'perfect',
        'superb', 'terrific', 'incredible', 'phenomenal', 'exceptional'
    ]
    
    # Negative words
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'worst', 'disappointing',
        'horrible', 'dreadful', 'atrocious', 'abysmal', 'pathetic',
        'useless', 'worthless', 'garbage', 'trash', 'mediocre'
    ]
    
    # Count occurrences
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    # Determine sentiment
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral' 