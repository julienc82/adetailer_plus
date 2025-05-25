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
    
    # Diviser le prompt en tokens (gérer les virgules, parenthèses, etc.)
    # Pattern pour capturer les mots tout en préservant la ponctuation
    tokens = re.findall(r'\([^)]*\)|\[[^\]]*\]|[^,\s]+|[,\s]+', prompt)
    
    cleaned_tokens = []
    for token in tokens:
        # Si c'est un token de ponctuation/espace, on le garde
        if re.match(r'^[,\s]+$', token):
            cleaned_tokens.append(token)
            continue
            
        # Si c'est une expression entre parenthèses/crochets, on traite l'intérieur
        if token.startswith('(') and token.endswith(')'):
            inner_content = token[1:-1]
            cleaned_inner = clean_prompt(inner_content, exclusion_words)
            if cleaned_inner.strip():  # Ne garder que si il reste du contenu
                cleaned_tokens.append(f'({cleaned_inner})')
            continue
            
        if token.startswith('[') and token.endswith(']'):
            inner_content = token[1:-1]
            cleaned_inner = clean_prompt(inner_content, exclusion_words)
            if cleaned_inner.strip():
                cleaned_tokens.append(f'[{cleaned_inner}]')
            continue
        
        # Pour les mots normaux, vérifier s'ils sont dans la liste d'exclusion
        word_lower = token.lower().strip()
        if word_lower not in exclusion_words:
            cleaned_tokens.append(token)
    
    # Reconstituer le prompt et nettoyer les espaces/virgules en trop
    result = ''.join(cleaned_tokens)
    
    # Nettoyer les virgules multiples et les espaces
    result = re.sub(r',\s*,+', ',', result)  # Virgules multiples
    result = re.sub(r'^\s*,\s*', '', result)  # Virgule au début
    result = re.sub(r'\s*,\s*$', '', result)  # Virgule à la fin
    result = re.sub(r'\s+', ' ', result)  # Espaces multiples
    
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
