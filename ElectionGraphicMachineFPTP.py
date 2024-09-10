import matplotlib.pyplot as plt
import numpy as np
import os
import random
import matplotlib.image as mpimg
from vote_calculations import calculate_vote_totals, determine_winner, calculate_lead_margin
from party_utils import get_leading_party


def update_total_votes(votes_by_riding, parties_by_riding, all_parties):
    for party_name, votes in zip(parties_by_riding, votes_by_riding):
        for party in all_parties:
            if party['name'] == party_name:
                party['pop_vote'] += votes  # Add the votes to the party's total
                break

def generate_individual_graphics(ridings, all_parties, num_graphics, num_selected_steps):
    # Sort ridings alphabetically by name

    sorted_ridings = ridings  # Keep the original order from the spreadsheet
    winner_determined = [False] * len(sorted_ridings)  # Track winner determination for each race
    winning_candidate_indices = [-1] * len(sorted_ridings)  # -1 indicates no winner yet
    winner_determined_steps = [None] * len(sorted_ridings)  # Initialize with None for each riding
    # Initialize party colors
    party_colors = {party['name']: party['color'] for party in all_parties}
    party_seat_counts = {party['name']: party['seats'] for party in all_parties}
    # Initialize vote totals matrix for each riding
    vote_totals_by_riding = [np.zeros((num_graphics, len(riding['final_results']))) for riding in sorted_ridings]
    previous_leading_party = None
    # Generate random vote totals for each candidate in each riding
    for r, riding in enumerate(sorted_ridings):
        num_parties = len(riding['final_results'])
        for j in range(num_parties):
            total_votes = riding['final_results'][j]
            vote_totals_by_riding[r][:, j] = calculate_vote_totals(total_votes, num_graphics)

        # Ensure final step has exact totals
        vote_totals_by_riding[r][-1] = riding['final_results']

        # Include step 0 where everyone has 0 votes
        vote_totals_by_riding[r][0] = np.zeros(num_parties)

    # Include steps at increments of 2.5%
    increments = np.linspace(0, 40, num=num_graphics)
    num_candidates = len(riding['candidate_names'])

    # Always include step 0 and step 40

    all_steps = list(range(1, num_graphics - 1))
    selected_steps = sorted(random.sample(all_steps, num_selected_steps - 2) + [0, num_graphics - 1])
    selected_steps.sort()

    # Check if output directory exists; if not, create it
    output_dir = 'output_images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the background image
    background_img = mpimg.imread('background.jpg')

    # Generate a separate image for each selected step for each riding
    for r, riding in enumerate(sorted_ridings):
        print(f'Starting processing for riding {riding["name"]}')
        # Track if seat counts have been updated for this riding
        seat_counts_updated = False
        previous_leading_party=None
        leading_party = None

        # Then loop through all steps for that specific riding
        for step in selected_steps:
            print(f'Starting graphics for step {step} for riding {riding["name"]}')
            try:
                # Calculate remaining votes for current step
                total_votes = np.sum(vote_totals_by_riding[r][step])
                remaining_votes = np.sum(riding['final_results']) - total_votes

                # Determine if winner is decided
                is_winner_determined = determine_winner(vote_totals_by_riding[r][step], remaining_votes)

                # Update the winning candidate index if a winner is determined and not already set
                if is_winner_determined and winning_candidate_indices[r] == -1:
                    winning_candidate_indices[r] = np.argmax(vote_totals_by_riding[r][step])
                    winner_determined_steps[r] = step  # Store the step where the winner was determined

                fig, ax = plt.subplots(figsize=(12, 8))

                # Ensure this line is added before saving each figure
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove any margins around the plot

                ax.imshow(background_img, aspect='auto', extent=[0, 1, 0, 1],
                          alpha=0.2)  # Make sure it covers the full area

                ax.axis('off')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)

                # Sort candidates by vote count for the current step
                sorted_indices = np.argsort(-vote_totals_by_riding[r][step])
                sorted_votes = vote_totals_by_riding[r][step][sorted_indices]
                sorted_names = np.array(riding['candidate_names'])[sorted_indices]
                sorted_parties = np.array(riding['party_names'])[sorted_indices]
                sorted_short_parties = np.array(riding['short_name'])[sorted_indices]
                sorted_colors = np.array([party_colors[party] for party in sorted_parties])

                total_votes_step = sorted_votes.sum()
                num_candidates = min(len(riding['candidate_names']), 4)
                width = 0.7 / 4
                padding = 0.1 / 4

                # Dimensions for the picture placeholder
                picture_width = width * 0.8
                picture_height = 0.35  # Height of the picture placeholder

                # Adjust y_pos for the picture box so it ends before the candidate information box


                # Limit to first 4 candidates
                max_displayed_candidates = 4
                num_candidates_to_display = min(len(sorted_votes), max_displayed_candidates)

                # Calculate the number of columns and rows needed
                num_displayed_columns = min(num_candidates_to_display, 4)  # Number of columns, up to a max of 4
                num_displayed_rows = (num_candidates_to_display - 1) // num_displayed_columns + 1  # Number of rows

                # Calculate the total width and height needed for the displayed candidate boxes
                total_width = num_displayed_columns * (width + padding) - padding  # Total width required for boxes
                total_height = num_displayed_rows * (
                            0.35 + picture_height)  # Total height required for boxes, including picture space

                # Calculate starting position to center the candidate block within the screen
                start_x = (1 - total_width) / 2  # Horizontal centering
                start_y = (1 - total_height) / 2  # Vertical centering

                for j in range(num_candidates_to_display):
                    col = j % num_displayed_columns
                    row = j // num_displayed_columns

                    # Calculate position for each candidate box
                    x_pos = start_x + col * (width + padding) + width / 2
                    y_pos = start_y + row * (0.45 + picture_height)  # Position adjusted for picture and info space
                    picture_y_pos = y_pos + 0.35  # Position it such that it starts at y_pos + 0.35 and ends before the information box
                    # Draw candidate's information box
                    rect = plt.Rectangle((x_pos - width / 2, y_pos), width, 0.35 + picture_height,
                                         color=sorted_colors[j],alpha=0.3, ec='black')
                    ax.add_patch(rect)

                    # Determine image path
                    candidate_image_path = f'facesteals/{sorted_names[j]}.jpg'
                    if not os.path.exists(candidate_image_path):
                        candidate_image_path = 'nopic.jpg'

                    # Load the image
                    image = plt.imread(candidate_image_path)

                    # Draw picture image above the candidate's information box
                    ax.imshow(image, extent=(x_pos - picture_width / 2 , x_pos + picture_width / 2 ,
                                             picture_y_pos - 0.05, picture_y_pos - 0.05 + picture_height),
                              aspect='auto', alpha=1, zorder=1)  # Ensure image is drawn on top

                    text_y_pos = y_pos + 0.15   # Center the text within the party color box

                    # Define text margin based on rank
                    lead_margin = calculate_lead_margin(sorted_votes, j,num_candidates_to_display)

                    displayed_votes = sorted_votes[j]

                    percentage_of_all = (sorted_votes[j] / total_votes_step) * 100 if total_votes_step > 0 else 0
                    if num_candidates_to_display <= 2:
                        dynamic_font_size_text = 14
                    elif num_candidates_to_display == 3:
                        dynamic_font_size_text = 14
                    else:
                        dynamic_font_size_text = 14

                    # Fixed Y position for the top of the text
                    fixed_y_pos = text_y_pos  # The same Y position for all text, no adjustment

                    # Generate the text with or without the lead margin
                    text = (f'{sorted_names[j]}\n'
                            f'{sorted_short_parties[j]}\n'
                            f'Votes: {int(sorted_votes[j])}\n'
                            f'{percentage_of_all:.1f}%')
                    if lead_margin > 0:
                        text += f'\n{int(lead_margin)} lead'

                    # Draw the text starting from the same Y position
                    ax.text(x_pos, fixed_y_pos+0.07, text, fontsize=dynamic_font_size_text, ha='center', va='top',
                            bbox=dict(facecolor='lightgray', alpha=0.5))

                    # Draw checkmark if the candidate is the winner
                    if winning_candidate_indices[r] != -1:
                        winning_index = winning_candidate_indices[r]

                        # Find the new index of the winning candidate in the sorted list
                        sorted_winning_index = np.where(sorted_indices == winning_index)[0][0]

                        # Only draw the checkmark if it's among the displayed candidates
                        if sorted_winning_index < max_displayed_candidates:
                            x_pos_check = start_x + (sorted_winning_index % num_displayed_columns) * (
                                        width + padding) + width / 2
                            y_pos_check = start_y + (sorted_winning_index // num_displayed_columns) * (
                                        0.35 + picture_height)

                            # Draw the checkmark closer to the right side of the candidate box
                            ax.text(x_pos_check + width / 2 - 0.005, y_pos_check + 0.35, '✓',
                                    fontsize=72, ha='right', va='top', color='green')

                # Draw progress bar
                progress_bar_x = 0.05
                progress_bar_y = 0.86
                progress_bar_width = 0.9
                progress_bar_height = 0.02
                progress = (step / (num_graphics - 1)) * 100

                bar_background = plt.Rectangle((progress_bar_x, progress_bar_y), progress_bar_width, progress_bar_height,
                                                color='lightgray', ec='black', alpha=0.8)
                ax.add_patch(bar_background)

                progress_bar = plt.Rectangle((progress_bar_x, progress_bar_y), (progress / 100) * progress_bar_width,
                                              progress_bar_height, color='blue', ec='black', alpha=0.8)
                ax.add_patch(progress_bar)

                ax.text(progress_bar_x + progress_bar_width / 2, progress_bar_y + progress_bar_height / 2,
                        f'{progress:.1f}%', fontsize=12, ha='center', va='center', weight='bold')

                # Add the riding name as a title above the progress bar
                ax.text(0.5, progress_bar_y + progress_bar_height + 0.01, f'{riding["name"]}',
                        fontsize=36, ha='center', va='bottom', weight='bold')

                # Create a dictionary for party seat counts using 'seats' from all_parties


                # Example vote data for the current riding (should come from your existing data structure)
                votes_by_riding = vote_totals_by_riding[r][step]
                parties_by_riding = np.array(riding['party_names'])[np.argsort(-votes_by_riding)]
                riding_name = riding['name']


                if np.any(votes_by_riding > 0):
                    leading_party = get_leading_party(votes_by_riding, parties_by_riding)

                    # Increment the seat count only if the leading party has changed and if not already updated
                    if leading_party != previous_leading_party:
                        # Update seat count for the previous leading party if it was set
                        if previous_leading_party and seat_counts_updated:
                            party_seat_counts[previous_leading_party] -= 1  # Remove seat from the previous leader
                            print(f"Decremented seat count for previous leading party: {previous_leading_party}")

                        # Update seat count for the new leading party
                        if leading_party:
                            party_seat_counts[leading_party] += 1
                            print(f"Incremented seat count for new leading party: {leading_party}")

                        # Mark seat counts as updated
                        seat_counts_updated = True
                        previous_leading_party = leading_party
                    else:
                        seat_counts_updated = False
                        print("Leading party has not changed; seat count not updated.")
                else:
                    seat_counts_updated = False
                    print("No votes available, seat counts not updated.")

                # Sort parties by seat count in descending order
                sorted_party_seat_counts = dict(
                    sorted(party_seat_counts.items(), key=lambda item: item[1], reverse=True))

                # Draw party seat counts
                seat_count_y_pos = y_pos - 0.25  # Positioning for the seat counts row
                seat_count_height = 0.2  # Height for the seat counts row
                padding = 0.03  # Reduced padding between party boxes
                num_parties = min(len(sorted_party_seat_counts), 6)  # Limit to first 6 parties for display
                party_width = 0.6 / num_parties  # Adjust width to fit more compactly
                total_width = num_parties * party_width + (num_parties - 1) * padding  # Total width including padding
                start_x = (1 - total_width) / 2  # Center the seat count boxes horizontally

                # Draw party boxes and seat counts
                for i, (party_name, count) in enumerate(
                        list(sorted_party_seat_counts.items())[:6]):  # Only take the first 6 parties

                    party_x_pos = start_x + i * (party_width + padding) + party_width / 2

                    # Draw the party box
                    party_box = plt.Rectangle((party_x_pos - party_width / 2, seat_count_y_pos),
                                              party_width, seat_count_height,
                                              color=party_colors.get(party_name, 'grey'),
                                              ec='black')  # Use 'grey' if color not found
                    ax.add_patch(party_box)

                    # Draw seat count text
                    ax.text(party_x_pos, seat_count_y_pos + seat_count_height / 2 + 0.03,
                            f'{count}', fontsize=20, ha='center', va='center', color='black')

                    # Draw party name text
                    ax.text(party_x_pos, seat_count_y_pos + seat_count_height / 2 + 0.07,
                            f'{party_name}', fontsize=8, ha='center', va='center', color='black')

                # Add background image last
                ax.imshow(background_img, aspect='auto', extent=[0, 1, 0, 1], alpha=0.3)

                # Remove the axis lines and labels
                ax.axis('off')

                # Set limits
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)

                # Save the figure
                filename = f'{riding["name"].replace(" ", "_")}_step_{step + 1:02}.png'
                filepath = os.path.join(output_dir, filename)
                plt.savefig(filepath, bbox_inches='tight')
                plt.close()

                # Generate line graph
                fig, ax = plt.subplots(figsize=(max(10, num_candidates * 2), 8))
                ax.set_title(f'Vote Progression in {riding["name"]}')
                ax.set_xlabel('Steps')
                ax.set_ylabel('Votes')

                for idx, candidate_name in enumerate(riding['candidate_names']):
                    ax.plot(increments, vote_totals_by_riding[r][:, idx], label=candidate_name,
                            color=party_colors[riding['party_names'][idx]])

                # Draw a horizontal dotted line at the step where the winner is determined
                if winner_determined_steps[r] is not None:
                    winner_step = winner_determined_steps[r]
                    ax.axvline(x=winner_step, color='red', linestyle='--', label='Winner Determined')

                ax.legend(loc='upper left')
                plt.grid(True)

                line_graph_filename = f'line_graph_riding_{r + 1:02}_{riding["name"].replace(" ", "_")}.png'
                line_graph_filepath = os.path.join(output_dir, line_graph_filename)
                plt.savefig(line_graph_filepath)
                plt.close()



            except Exception as e:

                print(f"Error processing step {step} for riding {riding['name']}: {e}")

            print(f'Completed all graphics for riding {riding["name"]}')

            print('Processed all ridings for all steps')

# Example usage
ridings = [
{ 'name': 'Toronto',
    'final_results': [999999, 599854],
    'candidate_names': ['PlayerA', 'PlayerB'],
    'party_names': ['Conservative Party of Canada', 'Liberal Party of Canada'],
    'short_name': ['CPC', 'LPC']
  }

]

all_parties = [
    {'name': 'Conservative Party of Canada', 'color': 'blue','seats':0,'pop_vote':0},
    {'name': 'Liberal Party of Canada', 'color': 'red','seats':0,'pop_vote':0},
    {'name': 'New Democratic Party', 'color': 'orange','seats':0,'pop_vote':0},
    {'name': 'Independent', 'color': 'gray','seats':0,'pop_vote':0}
]

generate_individual_graphics(ridings, all_parties, num_graphics=40, num_selected_steps=5)
