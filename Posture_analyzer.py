class FlatteringCutRecommender:
    def __init__(self):
        self.cut_rules = {
            # Shoulder-based recommendations
            "rounded_shoulders": {
                "tops": ["structured shoulders", "darted backs", "asymmetrical necklines"],
                "avoid": ["sloouchy sweaters", "heavy knits"],
                "reason": "Adds structure to correct rounded posture"
            },
            "uneven_shoulders": {
                "tops": ["off-shoulder (higher side)", "one-shoulder designs", "diagonal seams"],
                "avoid": ["horizontal stripes", "perfectly symmetrical cuts"],
                "reason": "Creates optical balance"
            },

            # Spinal curvature recommendations
            "kyphosis": {
                "tops": ["back interest details", "vertical seams", "wrap styles"],
                "dresses": ["empire waist", "surplice neckline"],
                "avoid": ["tight turtlenecks", "backless designs"],
                "reason": "Draws attention forward while supporting back"
            },

            # Head position recommendations
            "forward_head": {
                "tops": ["V-necks", "scoop necks", "vertical details"],
                "avoid": ["high necklines", "chokers"],
                "reason": "Elongates neck visually"
            },

            # Pelvic tilt recommendations
            "anterior_tilt": {
                "bottoms": ["high-waisted", "wide waistbands", "mid-rise"],
                "tops": ["hip-length", "tunic styles"],
                "avoid": ["low-rise pants", "cropped tops"],
                "reason": "Provides lumbar support"
            },
            "posterior_tilt": {
                "bottoms": ["contoured waistbands", "yoke details"],
                "tops": ["peplums", "ruched backs"],
                "avoid": ["baggy styles", "elastic-only waists"],
                "reason": "Creates waist definition"
            }
        }

    def analyze_posture_for_cuts(self, posture_data):
        """Main recommendation engine"""
        recommendations = {
            "tops": [],
            "bottoms": [],
            "dresses": [],
            "avoid": [],
            "rationale": []
        }

        # Shoulder analysis
        if posture_data["shoulder_slope_degrees"] > 5:
            rec = self.cut_rules["rounded_shoulders"]
            recommendations["tops"].extend(rec["tops"])
            recommendations["avoid"].extend(rec["avoid"])
            recommendations["rationale"].append(rec["reason"])

        # Spinal analysis
        if posture_data["spinal_curvature"] == "Kyphotic":
            rec = self.cut_rules["kyphosis"]
            for cat in rec:
                if cat in recommendations:
                    if isinstance(rec[cat], list):
                        recommendations[cat].extend(rec[cat])
                    else:
                        recommendations["rationale"].append(rec[cat])

        # Pelvic analysis
        if posture_data["pelvic_tilt"] == "Anterior":
            rec = self.cut_rules["anterior_tilt"]
            recommendations["bottoms"].extend(rec["bottoms"])
            recommendations["tops"].extend(rec["tops"])
            recommendations["rationale"].append(rec["reason"])

        return self._format_recommendations(recommendations)

    def _format_recommendations(self, raw_recs):
        """Remove duplicates and format output"""
        formatted = {}
        for category in raw_recs:
            if category == "rationale":
                formatted[category] = ". ".join(list(set(raw_recs[category]))) + "."
            else:
                formatted[category] = list(set(raw_recs[category]))

                # Add visual examples for top 3 recommendations
                if category in ["tops", "bottoms", "dresses"]:
                    formatted[f"{category}_visual"] = [
                        self._get_visual_reference(cut)
                        for cut in formatted[category][:3]
                    ]
        return formatted

    def _get_visual_reference(self, cut_name):
        """Mock function to get visual examples"""
        visual_db = {
            "structured shoulders": "shoulder_pad_example.jpg",
            "darted backs": "darted_back_diagram.png",
            "high-waisted": "high_waist_visual.jpg"
        }
        return visual_db.get(cut_name, "generic_cut.png")

