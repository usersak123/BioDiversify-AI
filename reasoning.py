def analyze_environment(profile):

    factors = []

    # Soil
    if profile.get("organic_carbon") is not None:
        if profile["organic_carbon"] < 1:
            factors.append(
                "Low soil organic carbon may indicate reduced "
                "soil biological activity and water-holding capacity."
            )

    if profile.get("soil_moisture") is not None:
        if profile["soil_moisture"] < 20:
            factors.append(
                "Low soil moisture can increase plant and "
                "soil-organism water stress."
            )

    # Climate
    if profile.get("rainfall") == "Low":
        factors.append(
            "Low rainfall can increase water stress and "
            "reduce suitable conditions for some organisms."
        )

    if profile.get("temperature") is not None:
        if profile["temperature"] > 30:
            factors.append(
                "High temperature can increase evaporative "
                "demand and environmental stress."
            )

    # Land use
    land_use = profile.get("land_use", "").lower()

    if "monoculture" in land_use:
        factors.append(
            "Monoculture reduces crop and habitat diversity "
            "within the managed area."
        )

    # Biodiversity
    if profile.get("species_richness") == "Low":
        factors.append(
            "Low species richness indicates reduced biodiversity."
        )

    if profile.get("habitat_diversity") == "Low":
        factors.append(
            "Low habitat diversity can reduce available "
            "ecological niches."
        )

    # Human impact
    if profile.get("pesticide_use") == "High":
        factors.append(
            "High pesticide pressure may affect non-target "
            "organisms depending on chemical and exposure."
        )

    return factors


def identify_interactions(profile):

    interactions = []

    rainfall = profile.get("rainfall")
    carbon = profile.get("organic_carbon")
    land_use = profile.get("land_use", "").lower()
    pesticide = profile.get("pesticide_use")

    if (
        rainfall == "Low"
        and carbon is not None
        and carbon < 1
    ):
        interactions.append(
            "Low rainfall + low soil organic carbon: "
            "reduced soil water retention may increase "
            "drought stress."
        )

    if (
        "monoculture" in land_use
        and profile.get("habitat_diversity") == "Low"
    ):
        interactions.append(
            "Monoculture + low habitat diversity: "
            "limited vegetation complexity can reduce "
            "available ecological niches."
        )

    if (
        pesticide == "High"
        and profile.get("species_richness") == "Low"
    ):
        interactions.append(
            "High pesticide pressure + low species richness: "
            "chemical pressure may compound existing biodiversity stress."
        )

    return interactions