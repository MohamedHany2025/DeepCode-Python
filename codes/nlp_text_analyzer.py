# NLP Text Analyzer - Advanced Natural Language Processing System
# Project: NLP Text Analyzer
# Language: Python
# Description: Advanced NLP system with sentiment analysis, entity recognition, and summarization

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import spacy
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# ==================== Enums ====================
class Sentiment(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class EntityType(Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    DATE = "DATE"
    MONEY = "MONEY"
    PERCENT = "PERCENT"

# ==================== Data Classes ====================
@dataclass
class SentimentResult:
    text: str
    sentiment: Sentiment
    confidence: float
    scores: Dict[str, float]

@dataclass
class Entity:
    text: str
    entity_type: EntityType
    start: int
    end: int

@dataclass
class NamedEntity:
    text: str
    label: str

@dataclass
class TextAnalysis:
    original_text: str
    sentiment: SentimentResult
    entities: List[Entity]
    named_entities: List[NamedEntity]
    summary: str
    keywords: List[str]
    word_count: int
    sentence_count: int

# ==================== Text Preprocessor ====================
class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from tokens"""
        return [token for token in tokens if token.lower() not in self.stop_words]

# ==================== Sentiment Analyzer ====================
class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.preprocessor = TextPreprocessor()
    
    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of text"""
        scores = self.vader.polarity_scores(text)
        compound = scores['compound']
        
        # Determine sentiment based on compound score
        if compound >= 0.75:
            sentiment = Sentiment.VERY_POSITIVE
        elif compound >= 0.25:
            sentiment = Sentiment.POSITIVE
        elif compound >= -0.25:
            sentiment = Sentiment.NEUTRAL
        elif compound >= -0.75:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.VERY_NEGATIVE
        
        confidence = abs(compound)
        
        return SentimentResult(
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            scores={
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': scores['compound']
            }
        )
    
    def analyze_sentences(self, text: str) -> List[SentimentResult]:
        """Analyze sentiment of each sentence"""
        sentences = sent_tokenize(text)
        return [self.analyze(sentence) for sentence in sentences]

# ==================== Named Entity Recognizer ====================
class NamedEntityRecognizer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spacy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def extract_entities(self, text: str) -> List[NamedEntity]:
        """Extract named entities from text"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append(NamedEntity(
                text=ent.text,
                label=ent.label_
            ))
        
        return entities
    
    def extract_person_names(self, text: str) -> List[str]:
        """Extract person names"""
        entities = self.extract_entities(text)
        return [ent.text for ent in entities if ent.label_ == 'PERSON']
    
    def extract_organizations(self, text: str) -> List[str]:
        """Extract organization names"""
        entities = self.extract_entities(text)
        return [ent.text for ent in entities if ent.label_ == 'ORG']
    
    def extract_locations(self, text: str) -> List[str]:
        """Extract location names"""
        entities = self.extract_entities(text)
        return [ent.text for ent in entities if ent.label_ == 'GPE']

# ==================== Text Summarizer ====================
class TextSummarizer:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
    
    def summarize(self, text: str, num_sentences: int = 3) -> str:
        """Summarize text using extractive summarization"""
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return text
        
        # Calculate word frequencies
        words = word_tokenize(text.lower())
        words = self.preprocessor.remove_stopwords(words)
        
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score sentences
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = word_tokenize(sentence.lower())
            words = self.preprocessor.remove_stopwords(words)
            
            score = sum(word_freq.get(word, 0) for word in words)
            sentence_scores[i] = score
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_sentences = sorted(top_sentences[:num_sentences], key=lambda x: x[0])
        
        summary = ' '.join([sentences[i] for i, _ in top_sentences])
        return summary

# ==================== Keyword Extractor ====================
class KeywordExtractor:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        words = word_tokenize(text.lower())
        words = self.preprocessor.remove_stopwords(words)
        
        # Calculate frequency
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_keywords[:num_keywords]]

# ==================== NLP Pipeline ====================
class TextAnalyzer:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ner = NamedEntityRecognizer()
        self.summarizer = TextSummarizer()
        self.keyword_extractor = KeywordExtractor()
    
    def analyze(self, text: str) -> TextAnalysis:
        """Complete text analysis"""
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze(text)
        
        # Named entity recognition
        named_entities = self.ner.extract_entities(text)
        
        # Convert to Entity objects
        entities = [
            Entity(
                text=ent.text,
                entity_type=EntityType[ent.label_],
                start=0,
                end=0
            )
            for ent in named_entities
            if ent.label_ in EntityType.__members__
        ]
        
        # Summary
        summary = self.summarizer.summarize(text, num_sentences=3)
        
        # Keywords
        keywords = self.keyword_extractor.extract_keywords(text, num_keywords=10)
        
        # Statistics
        word_count = len(word_tokenize(text))
        sentence_count = len(sent_tokenize(text))
        
        return TextAnalysis(
            original_text=text,
            sentiment=sentiment,
            entities=entities,
            named_entities=named_entities,
            summary=summary,
            keywords=keywords,
            word_count=word_count,
            sentence_count=sentence_count
        )

# ==================== Usage Example ====================
if __name__ == "__main__":
    analyzer = TextAnalyzer()
    
    sample_text = """
    Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
    The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
    I absolutely love their products and services. Apple has revolutionized the tech industry!
    Tim Cook is the current CEO, and the company continues to innovate and create amazing products.
    """
    
    result = analyzer.analyze(sample_text)
    
    print("=" * 60)
    print("NLP TEXT ANALYSIS RESULTS")
    print("=" * 60)
    
    print("\nSentiment Analysis:")
    print(f"  Sentiment: {result.sentiment.sentiment.value}")
    print(f"  Confidence: {result.sentiment.confidence:.2f}")
    print(f"  Scores: {result.sentiment.scores}")
    
    print("\nNamed Entities:")
    for ent in result.named_entities:
        print(f"  - {ent.text} ({ent.label})")
    
    print("\nSummary:")
    print(f"  {result.summary}")
    
    print("\nKeywords:")
    print(f"  {', '.join(result.keywords)}")
    
    print("\nStatistics:")
    print(f"  Word Count: {result.word_count}")
    print(f"  Sentence Count: {result.sentence_count}")
