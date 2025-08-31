import numpy as np
import pandas as pd
import os

# Set random seed for reproducibility
np.random.seed(100)

def get_weight(score: np.ndarray) -> np.ndarray:
    """Calculate weights for scores based on percentage thresholds."""
    conditions = [
        (score >= 75),
        (score >= 70),
        (score >= 65),
        (score >= 60),
        (score >= 55),
        (score >= 50),
        (score >= 45),
        (score >= 40)
    ]
    weights = [4.00, 3.50, 3.25, 3.00, 2.75, 2.50, 2.25, 2.00]
    return np.select(conditions, weights, default=0.00)

def generate_student_data(num_courses: int = 10) -> dict:
    """Generate data for one student."""
    # Generate scores from a normal distribution (mean=70, std=10), clipped to [40, 100]
    scores = np.clip(np.random.normal(70, 10, num_courses), 40, 100).astype(int)
    # Generate course units in [0, 3]
    course_units = np.array([round(np.random.random() * 3) for _ in range(num_courses)])
    # Generate single attendance (0–100%) and study time (0–12 hours)
    attendance = round(np.random.random() * 100)
    study_time = round(np.random.random() * 12)
    # Calculate weights
    weights = get_weight(scores)
    # Calculate weighted grade points (WGP)
    wgp = weights * course_units
    total_wgp = wgp.sum()
    # Calculate GPA (sum of weights / sum of course units, capped at 4.0)
    total_units = course_units.sum()
    gpa = min(round(total_wgp / total_units, 2), 4.00) if total_units > 0 else 0.00
    
    return {
        "scores": scores,
        "course_units": course_units,
        "weights": weights,
        "wgp": wgp,
        "attendance": attendance,
        "study_time": study_time,
        "gpa": gpa
    }

def random_score(num_students: int = 10000, num_courses: int = 10) -> pd.DataFrame:
    """Generate student performance data and save to CSV."""
    # Initialize lists for DataFrame
    all_scores = []
    all_weights = []
    all_wgp = []
    all_course_units = []
    all_attendance = []
    all_study_time = []
    all_gpa = []

    # Generate data for each student
    for _ in range(num_students):
        student = generate_student_data(num_courses)
        all_scores.append(student["scores"].sum())
        all_weights.append(student["weights"].sum())
        all_wgp.append(student["wgp"].sum())
        all_course_units.append(student["course_units"].sum())
        all_attendance.append(student["attendance"])
        all_study_time.append(student["study_time"])
        all_gpa.append(student["gpa"])
        
        # Optional: Print for debugging (commented out for large runs)
        # print(f"Scores: {student['scores']}, Units: {student['course_units']}")
        # print(f"Weight: {student['weights'].sum()}, Units: {student['course_units'].sum()}, GPA: {student['gpa']}")

    # Create DataFrame
    df = pd.DataFrame({
        "total_score": all_scores,
        "course_unit": all_course_units,
        "weight": all_weights,
        "wgp": all_wgp,
        "attendance": all_attendance,
        "study_time": all_study_time,
        "gpa": all_gpa
    })

    # Save to CSV
    base_path = os.path.abspath(os.getcwd())
    output_path = os.path.join(base_path, "app", "ml", "results.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    random_score(10000)