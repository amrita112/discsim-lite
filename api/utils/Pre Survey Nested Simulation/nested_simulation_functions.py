import numpy as np
import random
import matplotlib.pyplot as plt

def generate_real_scores_per_subject(num_students, mean, std_dev, granularity):
    """
    Generate real test scores for a single subject.
    """
    raw_scores = np.random.normal(loc=mean, scale=std_dev, size=num_students)
    raw_scores = np.clip(raw_scores, 0, 100)  # Ensure scores are between 0 and 100
    quantized_scores = np.round(raw_scores / (100 / (granularity - 1))) * (100 / (granularity - 1))
    return np.clip(quantized_scores, 0, 100)

def generate_real_scores(num_students, subjects_params):
    """
    Generate real test scores for multiple subjects.
    """
    real_scores = {}
    for subject, params in subjects_params.items():
        real_scores[subject] = generate_real_scores_per_subject(
            num_students, params['mean'], params['std_dev'], params['granularity']
        )
    return real_scores

def apply_integrity_distortion(scores, passing_mark, slope):
    """
    Apply integrity distortion to scores.
    
    Args:
        scores (np.ndarray): Array of real scores.
        passing_mark (float): Passing mark for the subject.
        slope (float): Slope of the distortion line.
    
    Returns:
        np.ndarray: Distorted scores with integrity distortion applied.
    """
    # Note: if the student has already got marks above passing, 
    # we are assuming that the marks will NOT be changed.
    distortion = np.maximum(0, passing_mark - scores) * slope
    distorted_scores = scores + distortion
    return np.clip(distorted_scores, 0, 100)

def apply_integrity_distortion_L0(real_scores, passing_marks, slope_L0):
    """
    Apply integrity distortion at L0 for all subjects.
    
    Args:
        real_scores (dict): Dictionary of real scores for each subject.
        passing_marks (dict): Dictionary of passing marks for each subject.
        slope_L0 (float): Slope for L0 integrity distortion.
    
    Returns:
        dict: Distorted scores with integrity distortion applied at L0.
    """
    distorted_scores = {}
    for subject, scores in real_scores.items():
        passing_mark = passing_marks[subject]
        distorted_scores[subject] = apply_integrity_distortion(scores, passing_mark, slope_L0)
    return distorted_scores

def apply_integrity_distortion_L1(real_scores, passing_marks, collusion_index, slope_L0):
    """
    Apply integrity distortion at L1 for all subjects.
    
    Args:
        real_scores (dict): Dictionary of real scores for each subject.
        passing_marks (dict): Dictionary of passing marks for each subject.
        collusion_index (float): Collusion index (0 to 1) for L1 integrity distortion.
        slope_L0 (float): Slope for L0 integrity distortion.
    
    Returns:
        dict: Distorted scores with integrity distortion applied at L1.
    """
    if not (0 <= collusion_index <= 1):
        raise ValueError("Collusion index must be between 0 and 1.")
    
    distorted_scores = {}
    for subject, scores in real_scores.items():
        passing_mark = passing_marks[subject]
        slope_L1 = slope_L0 * collusion_index  # Adjust slope based on collusion index
        distorted_scores[subject] = apply_integrity_distortion(scores, passing_mark, slope_L1)
    return distorted_scores

def apply_moderation_distortion(scores, moderation_index):
    """
    Apply moderation distortion to scores.
    
    Args:
        scores (np.ndarray): Array of scores to which moderation distortion will be applied.
        moderation_index (float): Value to be added to the scores as moderation.
    
    Returns:
        np.ndarray: Scores with moderation distortion applied.
    """
    moderated_scores = scores + moderation_index
    return np.clip(moderated_scores, 0, 100)

def apply_measurement_error(scores, mean=0, std_dev=1):
    """
    Apply measurement error to scores.
    
    Args:
        scores (np.ndarray): Array of scores to which measurement error will be applied.
        mean (float, optional): Mean of the normal distribution for measurement error. Default is 0.
        std_dev (float, optional): Standard deviation of the normal distribution for measurement error. Default is 1.
    
    Returns:
        np.ndarray: Scores with measurement error applied.
    """
    noise = np.random.normal(loc=mean, scale=std_dev, size=scores.shape)
    distorted_scores = scores + noise
    return np.clip(distorted_scores, 0, 100)

def apply_distortion_L0(real_scores, passing_marks, slope_L0, measurement_error_mean=0, measurement_error_std_dev=1):
    """
    Apply all distortions at L0.
    
    Args:
        real_scores (dict): Dictionary of real scores for each subject.
        passing_marks (dict): Dictionary of passing marks for each subject.
        slope_L0 (float): Slope for L0 integrity distortion.
        measurement_error_mean (float, optional): Mean of the normal distribution for measurement error. Default is 0.
        measurement_error_std_dev (float, optional): Standard deviation of the normal distribution for measurement error. Default is 1.
    
    Returns:
        dict: Distorted scores with all L0 distortions applied.
    """
    distorted_scores = apply_integrity_distortion_L0(real_scores, passing_marks, slope_L0)
    distorted_scores = {
        subject: apply_measurement_error(scores, mean=measurement_error_mean, std_dev=measurement_error_std_dev)
        for subject, scores in distorted_scores.items()
    }
    return distorted_scores

def apply_distortion_L1(real_scores, passing_marks, collusion_index, slope_L0, measurement_error_mean=0, measurement_error_std_dev=1, moderation_index_L1=0):
    """
    Apply all distortions at L1.
    
    Args:
        real_scores (dict): Dictionary of real scores for each subject.
        passing_marks (dict): Dictionary of passing marks for each subject.
        collusion_index (float): Collusion index (0 to 1) for L1 integrity distortion.
        slope_L0 (float): Slope for L0 integrity distortion.
        measurement_error_mean (float, optional): Mean of the normal distribution for measurement error. Default is 0.
        measurement_error_std_dev (float, optional): Standard deviation of the normal distribution for measurement error. Default is 1.
        moderation_index_L1 (float, optional): Moderation index for L1 distortion. Default is 0.
    
    Returns:
        dict: Distorted scores with all L1 distortions applied.
    """
    distorted_scores = apply_integrity_distortion_L1(real_scores, passing_marks, collusion_index, slope_L0)
    distorted_scores = {
        subject: apply_moderation_distortion(scores, moderation_index_L1) for subject, scores in distorted_scores.items()
    }
    distorted_scores = {
        subject: apply_measurement_error(scores, mean=measurement_error_mean, std_dev=measurement_error_std_dev)
        for subject, scores in distorted_scores.items()
    }
    return distorted_scores

def apply_distortion_L2(real_scores, measurement_error_mean=0, measurement_error_std_dev=1, moderation_index_L2=0):
    """
    Apply all distortions at L2.
    
    Args:
        real_scores (dict): Dictionary of real scores for each subject.
        measurement_error_mean (float, optional): Mean of the normal distribution for measurement error. Default is 0.
        measurement_error_std_dev (float, optional): Standard deviation of the normal distribution for measurement error. Default is 1.
        moderation_index_L2 (float, optional): Moderation index for L2 distortion. Default is 0.
    
    Returns:
        dict: Distorted scores with all L2 distortions applied.
    """
    distorted_scores = {
        subject: apply_moderation_distortion(scores, moderation_index_L2) for subject, scores in real_scores.items()
    }
    distorted_scores = {
        subject: apply_measurement_error(scores, mean=measurement_error_mean, std_dev=measurement_error_std_dev)
        for subject, scores in distorted_scores.items()
    }
    return distorted_scores

def simulate_test_scores(
    students_per_school, 
    subjects_params, 
    passing_marks, 
    n_schools_per_L1, 
    n_L1s_per_L2, 
    n_L2s, 
    L1_retest_percentage, 
    L2_retest_percentage_schools, 
    L2_retest_percentage_students, 
    collusion_index, 
    slope_L0=0.1, 
    moderation_index_L1=0, 
    moderation_index_L2=0, 
    measurement_error_mean=0, 
    measurement_error_std_dev=1
):
    """
    Simulate test scores through all levels for multiple subjects and hierarchical structure.

    Args:
        students_per_school (int): Number of students in each school.
        subjects_params (dict): Dictionary containing parameters for each subject.
        passing_marks (dict): Dictionary of passing marks for each subject.
        n_schools_per_L1 (int): Number of schools grouped into each L1 unit.
        n_L1s_per_L2 (int): Number of L1 units grouped into each L2 unit.
        n_L2s (int): Number of L2 units.
        L1_retest_percentage (float): Percentage of students retested at the L1 level (0 to 100).
        L2_retest_percentage_schools (float): Percentage of schools retested at the L2 level (0 to 100).
        L2_retest_percentage_students (float): Percentage of students retested at the L2 level (0 to 100).
        collusion_index (float): Collusion index for L1 integrity distortion (0 to 1).
        slope_L0 (float, optional): Slope for L0 integrity distortion. Default is 0.1.
        moderation_index_L1 (float, optional): Moderation index for L1 distortion. Default is 0.
        moderation_index_L2 (float, optional): Moderation index for L2 distortion. Default is 0.
        measurement_error_mean (float, optional): Mean of the normal distribution for measurement error. Default is 0.
        measurement_error_std_dev (float, optional): Standard deviation of the normal distribution for measurement error. Default is 1.

    Returns:
        dict: A nested dictionary containing simulated scores organized into L2, L1, and L0 units:
            {
                "L2_<l2_id>": {
                    "L1_<l1_id>": {
                        "school_<school_id>": {
                            "real_scores": Dict of real scores for each student in the school,
                            "L0_scores": Dict of L0 distorted scores for each student in the school,
                            "L1_scores": Dict of L1 distorted scores for retested students in the school,
                            "L2_scores": Dict of L2 distorted scores for retested students in the school
                        },
                        ...
                    },
                    ...
                },
                ...
            }
    """
    # Calculate the total number of schools
    num_schools = n_L2s * n_L1s_per_L2 * n_schools_per_L1

    # Generate unique student IDs
    student_ids = [f"student_{i}" for i in range(num_schools * students_per_school)]

    # Initialize the nested output structure
    nested_scores = {}

    # Generate real scores for all students
    real_scores = {}
    for student_id in student_ids:
        real_scores[student_id] = generate_real_scores(1, subjects_params)

    # Apply L0 distortions and organize by schools (L0 units)
    for l2_index in range(n_L2s):
        l2_key = f"L2_{l2_index}"
        nested_scores[l2_key] = {}

        for l1_index in range(n_L1s_per_L2):
            l1_key = f"L1_{l2_index}_{l1_index}"
            nested_scores[l2_key][l1_key] = {}

            # Get the schools in this L1 unit
            start_school = (l2_index * n_L1s_per_L2 + l1_index) * n_schools_per_L1
            end_school = start_school + n_schools_per_L1

            for school_index in range(start_school, end_school):
                school_key = f"school_{school_index}"
                start_student = school_index * students_per_school
                end_student = start_student + students_per_school
                school_student_ids = student_ids[start_student:end_student]

                # Get real scores and apply L0 distortions for this school
                school_real_scores = {student_id: real_scores[student_id] for student_id in school_student_ids}
                school_L0_scores = {
                    student_id: apply_distortion_L0(
                        real_scores[student_id], 
                        passing_marks, 
                        slope_L0=slope_L0, 
                        measurement_error_mean=measurement_error_mean, 
                        measurement_error_std_dev=measurement_error_std_dev
                    )
                    for student_id in school_student_ids
                }

                # Initialize the school dictionary
                nested_scores[l2_key][l1_key][school_key] = {
                    "real_scores": school_real_scores,
                    "L0_scores": school_L0_scores,
                    "L1_scores": {},
                    "L2_scores": {}
                }

    # Apply L1 distortions and organize by L1 units
    for l2_index in range(n_L2s):
        l2_key = f"L2_{l2_index}"

        for l1_index in range(n_L1s_per_L2):
            l1_key = f"L1_{l2_index}_{l1_index}"

            # Get the schools in this L1 unit
            start_school = (l2_index * n_L1s_per_L2 + l1_index) * n_schools_per_L1
            end_school = start_school + n_schools_per_L1

            for school_index in range(start_school, end_school):
                school_key = f"school_{school_index}"
                school_student_ids = list(nested_scores[l2_key][l1_key][school_key]["real_scores"].keys())

                # Select students for L1 retesting
                num_L1_retest = int(len(school_student_ids) * (L1_retest_percentage / 100))
                L1_retest_ids = random.sample(school_student_ids, num_L1_retest)

                # Apply L1 distortions for retested students
                school_L1_scores = {
                    student_id: apply_distortion_L1(
                        real_scores[student_id], 
                        passing_marks, 
                        collusion_index, 
                        slope_L0=slope_L0, 
                        measurement_error_mean=measurement_error_mean, 
                        measurement_error_std_dev=measurement_error_std_dev, 
                        moderation_index_L1=moderation_index_L1
                    )
                    for student_id in L1_retest_ids
                }

                # Store L1 scores in the nested structure
                nested_scores[l2_key][l1_key][school_key]["L1_scores"] = school_L1_scores

    # Apply L2 distortions and organize by L2 units
    for l2_index in range(n_L2s):
        l2_key = f"L2_{l2_index}"

        for l1_index in range(n_L1s_per_L2):
            l1_key = f"L1_{l2_index}_{l1_index}"

            # Get the schools in this L1 unit
            start_school = (l2_index * n_L1s_per_L2 + l1_index) * n_schools_per_L1
            end_school = start_school + n_schools_per_L1
            all_schools_in_L1 = list(range(start_school, end_school))

            # Select schools for L2 retesting from this L1 unit
            num_L2_retest_schools = int(len(all_schools_in_L1) * (L2_retest_percentage_schools / 100))
            L2_retest_schools = random.sample(all_schools_in_L1, num_L2_retest_schools)

            # Select students for L2 retesting from the selected schools
            for school_index in L2_retest_schools:
                school_key = f"school_{school_index}"
                school_student_ids = list(nested_scores[l2_key][l1_key][school_key]["L1_scores"].keys())

                # Select a subset of students for L2 retesting
                num_L2_retest_students = int(len(school_student_ids) * (L2_retest_percentage_students / 100))
                L2_retest_ids = random.sample(school_student_ids, num_L2_retest_students)

                # Apply L2 distortions for retested students
                school_L2_scores = {
                    student_id: apply_distortion_L2(
                        real_scores[student_id], 
                        measurement_error_mean=measurement_error_mean, 
                        measurement_error_std_dev=measurement_error_std_dev, 
                        moderation_index_L2=moderation_index_L2
                    )
                    for student_id in L2_retest_ids
                }

                # Store L2 scores in the nested structure
                nested_scores[l2_key][l1_key][school_key]["L2_scores"] = school_L2_scores

    return nested_scores

def combine_scores(groups):
    """
    Combine scores from multiple groups into a single dictionary.
    """
    combined_scores = {}
    for group in groups:
        for subject, scores in group.items():
            if subject not in combined_scores:
                combined_scores[subject] = []
            combined_scores[subject].extend(scores)
    for subject in combined_scores:
        combined_scores[subject] = np.array(combined_scores[subject])
    return combined_scores

def parse_nested_scores(nested_scores):
    """
    Parse the nested_scores dictionary to extract:
    1. A list of schools for each L1 that were retested by L2.
    2. A list of students in each of those schools that were retested by L2.
    3. A list of students in each school that was retested by L1.
    4. The length of each of these lists.

    Additionally, print:
    - 'L2 tested X students in Y schools' for each L1.
    - 'L1 tested Z students in each school' for each school.

    Args:
        nested_scores (dict): The nested dictionary containing scores organized by L2, L1, and schools.

    Returns:
        dict: A dictionary containing the parsed information.
    """
    result = {
        "L2_retested_schools": {},  # List of schools retested by L2 for each L1
        "L2_retested_students": {},  # List of students retested by L2 in each school
        "L1_retested_students": {},  # List of students retested by L1 in each school
        "lengths": {}  # Lengths of the above lists
    }

    for l2_key, l2_data in nested_scores.items():
        result["L2_retested_schools"][l2_key] = {}
        result["L2_retested_students"][l2_key] = {}
        result["L1_retested_students"][l2_key] = {}
        result["lengths"][l2_key] = {"L2_schools": {}, "L2_students": {}, "L1_students": {}}

        for l1_key, l1_data in l2_data.items():
            result["L2_retested_schools"][l2_key][l1_key] = []
            result["L2_retested_students"][l2_key][l1_key] = {}
            result["L1_retested_students"][l2_key][l1_key] = {}
            result["lengths"][l2_key]["L2_schools"][l1_key] = 0
            result["lengths"][l2_key]["L2_students"][l1_key] = {}
            result["lengths"][l2_key]["L1_students"][l1_key] = {}

            for school_key, school_data in l1_data.items():
                # Check if the school was retested by L2
                if school_data["L2_scores"]:
                    result["L2_retested_schools"][l2_key][l1_key].append(school_key)
                    result["L2_retested_students"][l2_key][l1_key][school_key] = list(school_data["L2_scores"].keys())
                    result["lengths"][l2_key]["L2_students"][l1_key][school_key] = len(school_data["L2_scores"])

                # Check if the school was retested by L1
                if school_data["L1_scores"]:
                    result["L1_retested_students"][l2_key][l1_key][school_key] = list(school_data["L1_scores"].keys())
                    result["lengths"][l2_key]["L1_students"][l1_key][school_key] = len(school_data["L1_scores"])

            # Update the length of L2 retested schools for this L1
            result["lengths"][l2_key]["L2_schools"][l1_key] = len(result["L2_retested_schools"][l2_key][l1_key])

            # Print the number of students retested by L1 in each school
            for school_key in result["L1_retested_students"][l2_key][l1_key]:
                num_students_L1 = result["lengths"][l2_key]["L1_students"][l1_key][school_key]
                print(f"L1 tested {num_students_L1} students in {school_key}")

        # Print the number of schools and students retested by L2 for each L1
        for l1_key in result["L2_retested_schools"][l2_key]:
            num_schools_L2 = result["lengths"][l2_key]["L2_schools"][l1_key]
            total_students_L2 = sum(
                result["lengths"][l2_key]["L2_students"][l1_key].get(school_key, 0)
                for school_key in result["L2_retested_students"][l2_key][l1_key]
            )
            print(f"L2 tested {total_students_L2} students in {num_schools_L2} schools for {l1_key}")

    return result

def plot_nested_scores(nested_scores, subjects):
    """
    Plot the distribution of real scores and compare them with L0, L1, and L2 scores.

    Args:
        nested_scores (dict): The nested dictionary containing scores organized by L2, L1, and schools.
        subjects (list): List of subjects to plot (e.g., ["Maths", "English", "Science"]).
    """
    # Collect all scores for each subject
    real_scores = {subject: [] for subject in subjects}
    L0_scores = {subject: [] for subject in subjects}
    L1_real_scores = {subject: [] for subject in subjects}
    L1_scores = {subject: [] for subject in subjects}
    L2_real_scores = {subject: [] for subject in subjects}
    L2_scores = {subject: [] for subject in subjects}

    # Traverse the nested_scores dictionary to extract scores
    for l2_data in nested_scores.values():
        for l1_data in l2_data.values():
            for school_data in l1_data.values():
                # Add real scores
                for student_scores in school_data["real_scores"].values():
                    for subject in subjects:
                        real_scores[subject].extend(student_scores[subject])  # Use extend to flatten arrays

                # Add L0 scores
                for student_scores in school_data["L0_scores"].values():
                    for subject in subjects:
                        L0_scores[subject].extend(student_scores[subject])  # Use extend to flatten arrays

                # Add L1 scores and corresponding real scores
                for student_id, student_scores in school_data["L1_scores"].items():
                    for subject in subjects:
                        L1_real_scores[subject].append(school_data["real_scores"][student_id][subject])
                        L1_scores[subject].append(student_scores[subject])

                # Add L2 scores and corresponding real scores
                for student_id, student_scores in school_data["L2_scores"].items():
                    for subject in subjects:
                        L2_real_scores[subject].append(school_data["real_scores"][student_id][subject])
                        L2_scores[subject].append(student_scores[subject])

    # Plot the distributions and comparisons
    num_subjects = len(subjects)
    fig, axes = plt.subplots(4, num_subjects, figsize=(5 * num_subjects, 20))

    for i, subject in enumerate(subjects):
        # Plot histogram of real scores
        axes[0, i].hist(real_scores[subject], bins=20, color="black", alpha=0.7)
        axes[0, i].set_title(f"Real Scores Distribution - {subject}")
        axes[0, i].set_xlabel("Score")
        axes[0, i].set_ylabel("Frequency")

        # Scatter plot: Real vs L0 scores
        axes[1, i].scatter(real_scores[subject], L0_scores[subject], alpha=0.5, color="blue")
        axes[1, i].set_title(f"Real vs L0 Scores - {subject}")
        axes[1, i].set_xlabel("Real Scores")
        axes[1, i].set_ylabel("L0 Scores")

        # Scatter plot: Real vs L1 scores
        axes[2, i].scatter(L1_real_scores[subject], L1_scores[subject], alpha=0.5, color="green")
        axes[2, i].set_title(f"Real vs L1 Scores - {subject}")
        axes[2, i].set_xlabel("Real Scores (L1 Retested)")
        axes[2, i].set_ylabel("L1 Scores")

        # Scatter plot: Real vs L2 scores
        axes[3, i].scatter(L2_real_scores[subject], L2_scores[subject], alpha=0.5, color="red")
        axes[3, i].set_title(f"Real vs L2 Scores - {subject}")
        axes[3, i].set_xlabel("Real Scores (L2 Retested)")
        axes[3, i].set_ylabel("L2 Scores")

    plt.tight_layout()
    plt.show()



