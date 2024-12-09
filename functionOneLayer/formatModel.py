from pydantic import BaseModel, Field
from openai import OpenAI
from typing import List, Dict, Any, Optional
import instructor
import os
from dotenv import load_dotenv

load_dotenv()

prompt = """
Context and Purpose:
You are an advanced AI assistant tasked with creating a precise user profile by analyzing video playlists. Our goal is to understand user interests, learning patterns, and characteristics through intelligent video content analysis.
All the playlists is from one Youtube user's favorite playlist.

Analysis Framework:
When examining the provided playlist, consider these key aspects:

Playlist Analysis Strategy:

1. Playlist Weight Distribution:
- Small playlists (1-5 videos): High weight (Consider as carefully curated content)
- Medium playlists (6-15 videos): Medium weight
- Large playlists (15+ videos): Lower weight per video to avoid overrepresentation
-Each playlist may indicate the user's information aspect,so pay attention to all the playlists.

2. Quality Assessment:
- Look for theme clusters within playlists
- Identify consistent interests vs. random exploration
- Consider video recency and temporal patterns
- Pay special attention to recently added videos

3. Cross-Validation Points:
- Find common themes across different playlist sizes
- Look for age-specific indicators across multiple videos
- Consider content sophistication level
- Evaluate language patterns and content complexity

Core Objectives:
1. Demographic Prediction (High Precision Focus):
- Age Range Detection (Primary focus - must be well-justified)
- Gender Likelihood
- Potential Geographical Inference

2. Interest Analysis:
- Primary interest clusters
- Skill/Knowledge level indicators
- Content consumption patterns

Confidence Score Mechanism:
- Low Confidence (25-40%): Limited indicators
- Medium Confidence (40-70%): Multiple supporting factors
- High Confidence (70-100%): Strong consistent evidence

Output Guidelines:
- Prioritize quality over quantity in analysis
- Focus on strong patterns rather than outliers
- Consider temporal aspects of content
- Weight recent content more heavily

Response Format:
The response should be a structured profile with the following components:

1. Summary: A brief, engaging description of the user (2-3 sentences)

2. Core Identity:
   - Age range (in a 5-10 year span)
   - Generation identifier (e.g., Gen-Z, 90s)
   - Broad geographical region
   
3. Identity Tags: 5-8 key tags that define the user (e.g., "Tech Enthusiast", "Anime Lover")

4. Interests:
   - Professional interests (3-5 items)
   - Entertainment interests (3-5 items)

5. Content Preferences:
   - Preferred languages
   - Overall content style
   
6. Expertise Areas: Key areas with levels (e.g., "Programming: Advanced")

7. Confidence Scores:
   - Overall confidence
   - Interests confidence
   - Location confidence
   - Age confidence

Example Response:
(The response match our UserProfile BaseModel format)
{
    "summary": "A tech-savvy Gen-Z developer with a passion for anime and gaming. Shows strong interest in frontend development and UI/UX design, while maintaining active engagement in gaming communities.",
    "age_range": "20-25",
    "generation": "Gen-Z",
    "region": "East Asia",
    "identity_tags": [
        "Tech Enthusiast",
        "Anime Lover",
        "Code Wizard",
        "Digital Native",
        "Creative Mind"
    ],
    "professional_interests": [
        "Frontend Development",
        "UI/UX Design",
        "Software Engineering"
    ],
    "entertainment_interests": [
        "Anime",
        "Gaming",
        "Tech Reviews"
    ],
    "languages": ["Chinese", "English", "Japanese"],
    "content_preference": "Technical tutorials mixed with entertainment content, preference for visual learning",
    "expertise_areas": {
        "programming": "Intermediate",
        "design": "Beginner",
        "gaming": "Advanced"
    },
    "confidence_scores": {
        "overall": 0.85,
        "interests": 0.9,
        "location": 0.7,
        "age": 0.8
    }
}

Remember:
- Maintain consistency in analysis
- Provide clear justification for confidence scores
- Keep the format structured and clean
- Use natural, engaging language in the summary
"""

class UserProfile(BaseModel):
    # Core Summary
    summary: str = Field(description="A brief, engaging summary of the user's profile")
    
    # Identity Information
    age_range: str = Field(description="Age range the user are most likely to be")
    generation: str = Field(description="Generation identifier (e.g., 'Gen-Z', '90s')")
    region: str = Field(description="Broad geographical region (e.g., 'East Asia')")
    
    # Tags and Interests
    identity_tags: List[str] = Field(description="Key identifying tags for the user")
    professional_interests: List[str] = Field(description="Professional or learning interests")
    entertainment_interests: List[str] = Field(description="Entertainment and hobby interests")
    
    # Cultural and Content
    languages: List[str] = Field(description="Content languages preferred by user")
    content_preference: str = Field(description="Overall content consumption style and preferences")
    
    # Expertise
    expertise_areas: dict[str, str] = Field(description="Key areas and their expertise levels")
    
    # Confidence Scores (only for major categories)
    confidence_scores: dict[str, float] = Field(
        description="Confidence scores for major categories (overall, interests, location, age), eg:{'overall': 0.85, 'interests': 0.9, 'location': 0.7, 'age': 0.8}"
    )
    
    def __str__(self) -> str:
        return f"""
User Profile Analysis
--------------------
Summary: {self.summary}

Core Identity:
Age Range: {self.age_range}
Generation: {self.generation}
Region: {self.region}

Identity Tags: {', '.join(self.identity_tags)}

Professional Interests: {', '.join(self.professional_interests)}
Entertainment Interests: {', '.join(self.entertainment_interests)}

Languages: {', '.join(self.languages)}
Content Preference: {self.content_preference}

Expertise Areas:
{chr(10).join(f'- {k}: {v}' for k, v in self.expertise_areas.items())}

Confidence Scores:
{chr(10).join(f'- {k}: {v:.2f}' for k, v in self.confidence_scores.items())}
"""

client_format = instructor.patch(OpenAI(
    #base_url=os.getenv('OPENAI_BASE_URL'),
    api_key=os.getenv('OPENAI_API_KEY'),
))

def get_formatted_profile(input_text: str) -> UserProfile:
    response = client_format.chat.completions.create(
        model="gpt-4o-mini",
        response_model=UserProfile,
        max_retries=3,
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text}
        ]
    )
    
    return response
