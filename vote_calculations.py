import numpy as np

def calculate_vote_totals(total_votes, num_steps=40):
    random_numbers = np.random.rand(num_steps)
    cumulative_sum = np.cumsum(random_numbers)
    total_sum = cumulative_sum[-1]
    percentages = cumulative_sum / total_sum
    vote_totals = total_votes * percentages
    return vote_totals

def determine_winner(vote_totals, remaining_votes, threshold=0.4):
    if len(vote_totals) == 1:
        # If there's only one candidate, they are the winner
        return True

    # Sort the vote totals in descending order
    sorted_totals = sorted(vote_totals, reverse=True)
    leading_total = sorted_totals[0]
    second_place_total = sorted_totals[1]

    # Calculate the margin and the maximum possible for the second place candidate
    margin = leading_total - second_place_total
    max_possible_for_other = second_place_total + remaining_votes

    # Calculate the percentage of remaining votes needed for the second place candidate to potentially win
    percentage_needed = (leading_total - second_place_total) / remaining_votes if remaining_votes > 0 else 0


    # Call the election if there are no remaining votes
    if remaining_votes == 0:
        print("No remaining votes. Winner determined: True")
        return True

    # Determine if the second place candidate would need more than the threshold percentage of the remaining votes
    if percentage_needed > threshold:
        print("Winner determined: True")
        return True
    else:
        print("Winner determined: False")
        return False

# Define the margin for the leader
def calculate_lead_margin(votes, rank,num_candidates_to_display):
    if rank == 0 and num_candidates_to_display > 1:  # Leader
        lead_margin = votes[0] - votes[1] if len(votes) > 1 else 0
        return lead_margin
    return 0