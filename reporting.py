# Import required libraries
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from main_v9 import (
    create_geotype,
    deploy_radio_equipment,
    calculate_total_cost,
    calculate_cost_component,
    soluzione_1_with_smallcellswitch,
    soluzione_2_with_smallcellmux,
    soluzione_3_with_smallcellaggr,
)


# Function to compute costs and generate stacked charts
def generate_stacked_cost_plot(T, term, scenario, save_path):
    solution_funcs = [
        ('Electronic', soluzione_1_with_smallcellswitch),
        ('WDM', soluzione_2_with_smallcellmux),
        ('P2MP', soluzione_3_with_smallcellaggr)
    ]

    cost_data = []

    for name, func in solution_funcs:
        func(T)
        total_cost = calculate_total_cost(T)
        transceiver_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE"])
        switching_cost = total_cost - transceiver_cost
        cost_data.append({
            'Solution': name,
            'Transceiver Cost': transceiver_cost,
            'Switching Elements Cost': switching_cost,
            'Total Cost': total_cost,
            'Term': term
        })

    df = pd.DataFrame(cost_data)

    df.set_index('Solution', inplace=True)
    df[['Transceiver Cost', 'Switching Elements Cost']].plot(kind='bar', stacked=True, figsize=(10, 7),
                                                             color=['#FF9999', '#66B2FF'])
    plt.title(f'{term.capitalize()} Term Cost Breakdown for {scenario} Scenario')
    plt.ylabel('Total Cost (Cost Units)')
    plt.xlabel('Solution')
    plt.legend(loc='upper left')
    plt.grid(True)

    plt.savefig(save_path)
    plt.close()


# Function to create the PDF report
def create_report_pdf(output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Generate Dense Urban topology (T, T_m)
    T, T_m, _ = create_geotype('Dense Urban')

    # Report title
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Report per scenario Dense Urban', ln=True, align='C')

    # Add topology image
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Topologia Dense Urban con Nodi Corner (T_m)', ln=True, align='C')
    pdf.ln(10)
    pdf.image('dense_urban_topology.png', x=30, w=150)

    # Add cost chart (short term)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Short Term Cost Breakdown', ln=True, align='C')
    pdf.ln(10)
    generate_stacked_cost_plot(T, 'medium', 'Dense Urban', 'short_term_cost_breakdown.png')
    pdf.image('short_term_cost_breakdown.png', x=30, w=150)

    # Add cost chart (long term)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Long Term Cost Breakdown', ln=True, align='C')
    pdf.ln(10)
    generate_stacked_cost_plot(T, 'long', 'Dense Urban', 'long_term_cost_breakdown.png')
    pdf.image('long_term_cost_breakdown.png', x=30, w=150)

    # Save the PDF
    pdf.output(output_path)


# Run the function to create the report
create_report_pdf('Dense_Urban_Report.pdf')
