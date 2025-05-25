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
    Nettoie un prompt en supprimant les mots d'exclusion.
    
    Args:
        prompt: Le prompt original
        exclusion_words: Set des mots à exclure
        
    Returns:
        Prompt nettoyé
    """
    if not prompt or not exclusion_words:
        return prompt
    
    result = prompt
    
    # Traiter d'abord les expressions entre parenthèses et crochets
    def clean_bracketed_content(match):
        bracket_type = match.group(1)  # '(' ou '['
        content = match.group(2)
        closing_bracket = ')' if bracket_type == '(' else ']'
        
        # Nettoyer récursivement le contenu
        cleaned_content = clean_prompt_with_exclusions(content, exclusion_words)
        
        # Si le contenu nettoyé est vide, supprimer complètement
        if not cleaned_content.strip():
            return ''
        
        return f'{bracket_type}{cleaned_content}{closing_bracket}'
    
    # Pattern pour capturer les expressions entre parenthèses/crochets avec leur contenu
    result = re.sub(r'([\(\[])(.*?)([\)\]])', clean_bracketed_content, result)
    
    # Diviser le prompt en segments séparés par des virgules
    segments = [segment.strip() for segment in result.split(',')]
    cleaned_segments = []
    
    for segment in segments:
        if not segment:
            continue
            
        # Vérifier si ce segment (ou une partie) doit être exclu
        segment_should_be_kept = True
        segment_lower = segment.lower()
        
        # Vérifier chaque mot/expression d'exclusion
        for exclusion in exclusion_words:
            exclusion_lower = exclusion.lower()
            
            # Vérification exacte du segment complet
            if segment_lower == exclusion_lower:
                segment_should_be_kept = False
                break
            
            # Vérification si l'expression d'exclusion est contenue dans le segment
            # On utilise des word boundaries pour éviter les correspondances partielles
            # mais on permet les espaces dans l'expression
            exclusion_pattern = r'\b' + re.escape(exclusion_lower) + r'\b'
            if re.search(exclusion_pattern, segment_lower):
                # Remplacer l'expression trouvée par une chaîne vide
                segment = re.sub(exclusion_pattern, '', segment, flags=re.IGNORECASE)
                segment = segment.strip()
                
                # Si le segment devient vide après suppression, ne pas le garder
                if not segment:
                    segment_should_be_kept = False
                    break
        
        if segment_should_be_kept and segment.strip():
            cleaned_segments.append(segment.strip())
    
    # Reconstituer le prompt
    result = ', '.join(cleaned_segments)
    
    # Nettoyer les espaces multiples et autres artefacts
    result = re.sub(r'\s+', ' ', result)  # Espaces multiples
    result = re.sub(r'\s*,\s*', ', ', result)  # Normaliser les espaces autour des virgules
    result = result.strip().strip(',').strip()  # Supprimer les virgules en début/fin
    
    return result


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
