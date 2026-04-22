"""
Match Scoring Service - Calculates match scores for donors based on requests.
"""
import math
from typing import Dict, Any, Optional, List
from app.domain.entities import BloodRequest, UserProfile
from app.repositories.factory import get_donation_repository
import logging

logger = logging.getLogger(__name__)

# Match score weights
DISTANCE_WEIGHT = 0.35
BLOOD_TYPE_WEIGHT = 0.40
ELIGIBILITY_WEIGHT = 0.15
RELIABILITY_WEIGHT = 0.10

# Blood type compatibility matrix
BLOOD_COMPATIBILITY = {
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"]
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (in kilometers).
    Uses the Haversine formula.
    """
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')  # Return infinity if location data is missing
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    return R * c


def calculate_distance_score(distance_km: float) -> float:
    """
    Calculate distance score (0-100).
    Closer donors get higher scores.
    """
    if distance_km == float('inf'):
        return 0.0
    
    # Maximum distance to consider (100km)
    max_distance = 100.0
    
    if distance_km > max_distance:
        return 0.0
    
    # Linear scoring: 100km = 0, 0km = 100
    score = 100.0 * (1 - (distance_km / max_distance))
    return max(0.0, min(100.0, score))


def calculate_blood_type_score(donor_blood_group: Optional[str], required_blood_group: str) -> float:
    """
    Calculate blood type compatibility score (0-100).
    Exact match = 100, compatible = 80, incompatible = 0
    """
    if not donor_blood_group:
        return 0.0
    
    if donor_blood_group == required_blood_group:
        return 100.0  # Exact match
    
    # Check compatibility
    compatible_groups = BLOOD_COMPATIBILITY.get(donor_blood_group, [])
    if required_blood_group in compatible_groups:
        return 80.0  # Compatible but not exact
    
    return 0.0  # Incompatible


def calculate_eligibility_score(donor: UserProfile, request: BloodRequest) -> float:
    """
    Calculate eligibility score (0-100) based on:
    - Availability status
    - City match
    - Gender match (if specified)
    """
    score = 0.0
    
    # Availability (50 points)
    if donor.available and donor.mode == "donor":
        score += 50.0
    else:
        return 0.0  # Not available or not a donor
    
    # City match (30 points)
    if donor.city and request.city and donor.city.lower() == request.city.lower():
        score += 30.0
    elif donor.city and request.city:
        # Same province/region (simplified - could be enhanced)
        score += 10.0
    
    # Gender match (20 points) - if specified in request
    if request.gender and donor.gender:
        if donor.gender.lower() == request.gender.lower():
            score += 20.0
    
    return min(100.0, score)


async def calculate_reliability_score(donor_id: str) -> float:
    """
    Calculate reliability score (0-100) based on donation history.
    Factors:
    - Total donations completed
    - Acceptance rate (accepted vs rejected requests)
    - Recent activity
    """
    try:
        donation_repo = get_donation_repository()
        
        # Get all donations for this donor
        donations = await donation_repo.list_user_donations(donor_id)
        
        # Count completed donations
        completed_donations = len([d for d in donations if d.status == "donated"])
        
        # Base score from completed donations (max 60 points)
        donation_score = min(60.0, completed_donations * 10.0)
        
        # Acceptance rate (max 40 points)
        # This would require request repository to get acceptance stats
        # For now, use donation completion rate
        total_donations = len(donations)
        if total_donations > 0:
            completion_rate = completed_donations / total_donations
            acceptance_score = completion_rate * 40.0
        else:
            acceptance_score = 20.0  # Default score for new donors
        
        total_score = donation_score + acceptance_score
        return min(100.0, total_score)
        
    except Exception as e:
        logger.error(f"Error calculating reliability score for donor {donor_id}: {e}")
        return 50.0  # Default score on error


async def calculate_match_score(
    donor: UserProfile,
    request: BloodRequest,
    donation_repo=None
) -> Dict[str, Any]:
    """
    Calculate overall match score for a donor-request pair.
    
    Returns:
        Dictionary with match score and component scores
    """
    try:
        # Calculate distance score
        distance_km = float('inf')
        if (request.locationLat and request.locationLng and 
            donor.locationLat and donor.locationLng):
            distance_km = haversine_distance(
                request.locationLat, request.locationLng,
                donor.locationLat, donor.locationLng
            )
        
        distance_score = calculate_distance_score(distance_km)
        
        # Calculate blood type score
        blood_type_score = calculate_blood_type_score(
            donor.bloodGroup,
            request.requiredBloodGroup
        )
        
        # Calculate eligibility score
        eligibility_score = calculate_eligibility_score(donor, request)
        
        # Calculate reliability score
        reliability_score = await calculate_reliability_score(donor.uid)
        
        # Calculate weighted match score
        match_score = (
            (DISTANCE_WEIGHT * distance_score) +
            (BLOOD_TYPE_WEIGHT * blood_type_score) +
            (ELIGIBILITY_WEIGHT * eligibility_score) +
            (RELIABILITY_WEIGHT * reliability_score)
        )
        
        return {
            "matchScore": round(match_score, 2),
            "distanceKm": round(distance_km, 2) if distance_km != float('inf') else None,
            "distanceScore": round(distance_score, 2),
            "bloodTypeScore": round(blood_type_score, 2),
            "eligibilityScore": round(eligibility_score, 2),
            "reliabilityScore": round(reliability_score, 2),
            "weights": {
                "distance": DISTANCE_WEIGHT,
                "bloodType": BLOOD_TYPE_WEIGHT,
                "eligibility": ELIGIBILITY_WEIGHT,
                "reliability": RELIABILITY_WEIGHT
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating match score: {e}", exc_info=True)
        return {
            "matchScore": 0.0,
            "distanceKm": None,
            "distanceScore": 0.0,
            "bloodTypeScore": 0.0,
            "eligibilityScore": 0.0,
            "reliabilityScore": 0.0,
            "error": str(e)
        }


async def calculate_match_scores_for_request(
    request: BloodRequest,
    donors: List[UserProfile]
) -> List[Dict[str, Any]]:
    """
    Calculate match scores for multiple donors against a request.
    Returns list of donors with their match scores, sorted by score (descending).
    """
    results = []
    
    for donor in donors:
        match_data = await calculate_match_score(donor, request)
        results.append({
            "donor": donor,
            **match_data
        })
    
    # Sort by match score (descending)
    results.sort(key=lambda x: x["matchScore"], reverse=True)
    
    return results

