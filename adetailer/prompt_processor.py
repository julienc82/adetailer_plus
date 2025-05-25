import re
from typing import List, Set


def parse_exclusion_words(exclusion_text: str) -> Set[str]:
    """
    Parse la liste d'exclusion et retourne un ensemble de mots à exclure.
    
    Args:
        exclusion_text: Texte contenant les mots à exclure (un par ligne)
        
    Returns:
        Set[str]: Ensemble des mots à exclure (en minuscules)
    """
    if not exclusion_text:
        return set()
    
    # Séparer par lignes et nettoyer
    words = [line.strip().lower() for line in exclusion_text.splitlines()]
    # Retirer les lignes vides
    words = [w for w in words if w]
    
    return set(words)


def clean_prompt_with_exclusions(prompt: str, exclusion_words: Set[str]) -> str:
    """
    Nettoie un prompt en retirant les mots de la liste d'exclusion.
    
    Args:
        prompt: Le prompt à nettoyer
        exclusion_words: Ensemble des mots à exclure
        
    Returns:
        str: Le prompt nettoyé
    """
    if not prompt or not exclusion_words:
        return prompt
    
    # Fonction pour vérifier si un mot doit être exclu
    def should_exclude(word: str) -> bool:
        return word.lower() in exclusion_words
    
    # Traiter le prompt par segments (entre virgules)
    segments = prompt.split(',')
    cleaned_segments = []
    
    for segment in segments:
        # Séparer les mots tout en gardant la ponctuation et les espaces
        words = re.findall(r'\S+|\s+', segment)
        
        cleaned_words = []
        for word in words:
            # Si c'est un espace ou de la ponctuation, le garder
            if word.isspace() or not word.strip():
                cleaned_words.append(word)
                continue
            
            # Extraire le mot sans ponctuation pour la comparaison
            word_clean = re.sub(r'[^\w\s-]', '', word)
            
            # Si le mot n'est pas dans la liste d'exclusion, le garder
            if not should_exclude(word_clean):
                cleaned_words.append(word)
        
        # Reconstruire le segment
        cleaned_segment = ''.join(cleaned_words).strip()
        if cleaned_segment:
            cleaned_segments.append(cleaned_segment)
    
    # Rejoindre les segments avec des virgules
    result = ', '.join(cleaned_segments)
    
    # Nettoyer les espaces multiples
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*,\s*', ', ', result)
    
    return result.strip()


def process_prompt_with_exclusions(prompt: str, exclusion_text: str) -> str:
    """
    Fonction principale pour traiter un prompt avec une liste d'exclusion.
    
    Args:
        prompt: Le prompt à traiter
        exclusion_text: Le texte contenant les mots à exclure
        
    Returns:
        str: Le prompt traité
    """
    if not exclusion_text:
        return prompt
    
    exclusion_words = parse_exclusion_words(exclusion_text)
    return clean_prompt_with_exclusions(prompt, exclusion_words)
