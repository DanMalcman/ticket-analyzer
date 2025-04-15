
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

class TicketAnalyzer:
    def __init__(self):
        self.df_viv = None
        self.df_fortress = None
        self.df_merged = None
        self.results = {}

    def load_files(self, viv_file, fortress_file):
        try:
            self.df_viv = pd.read_excel(viv_file) if viv_file.name.endswith('.xlsx') else pd.read_csv(viv_file)
            self.df_fortress = pd.read_excel(fortress_file) if fortress_file.name.endswith('.xlsx') else pd.read_csv(fortress_file)

            if 'barcode' not in self.df_viv.columns:
                st.error("⚠️ קובץ הכרטיסים הראשי חייב לכלול עמודת 'barcode'")
                return False
            if 'Barcode' not in self.df_fortress.columns:
                st.error("⚠️ קובץ נתוני הכניסה חייב לכלול עמודת 'Barcode'")
                return False

            return True
        except Exception as e:
            st.error(f"שגיאה בטעינת הקבצים: {e}")
            return False

    def analyze_tickets(self):
        try:
            self.df_merged = pd.merge(self.df_viv, self.df_fortress, left_on='barcode', right_on='Barcode', how='left')
            self.df_merged['Entered to the game?'] = self.df_merged['Barcode'].apply(lambda x: 'V' if pd.notna(x) else 'X')

            has_ticket_name = 'ticketName' in self.df_merged.columns
            entered = self.df_merged[self.df_merged['Entered to the game?'] == 'V']
            not_entered = self.df_merged[self.df_merged['Entered to the game?'] == 'X']

            if has_ticket_name:
                entered_regular = entered[~entered['ticketName'].str.contains('מנוי', na=False)]
                entered_season = entered[entered['ticketName'].str.contains('מנוי', na=False)]
                not_entered_regular = not_entered[~not_entered['ticketName'].str.contains('מנוי', na=False)]
                not_entered_season = not_entered[not_entered['ticketName'].str.contains('מנוי', na=False)]

                self.results = {
                    'total_tickets': len(self.df_merged),
                    'total_entered': len(entered),
                    'total_not_entered': len(not_entered),
                    'entered_regular': len(entered_regular),
                    'entered_season': len(entered_season),
                    'not_entered_regular': len(not_entered_regular),
                    'not_entered_season': len(not_entered_season),
                    'entry_rate': f"{(len(entered) / len(self.df_merged) * 100):.1f}%",
                    'has_ticket_name': has_ticket_name
                }
            else:
                self.results = {
                    'total_tickets': len(self.df_merged),
                    'total_entered': len(entered),
                    'total_not_entered': len(not_entered),
                    'entry_rate': f"{(len(entered) / len(self.df_merged) * 100):.1f}%",
                    'has_ticket_name': has_ticket_name
                }
            return True
        except Exception as e:
            st.error(f"שגיאה בזמן ניתוח: {e}")
            return False

    def display_results(self):
        if not self.results:
            st.warning("לא בוצע ניתוח. אנא טען קבצים ולחץ על 'נתח כרטיסים'.")
            return

        st.subheader("📊 תוצאות ניתוח כרטיסים")

        fig, ax = plt.subplots()
        labels = ['נכנסו', 'לא נכנסו']
        sizes = [self.results['total_entered'], self.results['total_not_entered']]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        if self.results['has_ticket_name']:
            st.write(f"🎟️ **כרטיסים רגילים שנכנסו:** {self.results['entered_regular']}")
            st.write(f"🎟️ **כרטיסים ממנוי שנכנסו:** {self.results['entered_season']}")
            st.write(f"🚫 **כרטיסים רגילים שלא נכנסו:** {self.results['not_entered_regular']}")
            st.write(f"🚫 **כרטיסים ממנוי שלא נכנסו:** {self.results['not_entered_season']}")
        st.success(f"סה"כ נכנסו: {self.results['total_entered']} מתוך {self.results['total_tickets']} ({self.results['entry_rate']})")

def main():
    st.set_page_config(page_title="ניתוח כרטיסים", page_icon="🎟️", layout="centered")
    st.title("🎟️ אפליקציית ניתוח כרטיסים")
    st.write("העלה קבצי נתונים כדי לנתח את הכניסות לאירוע שלך!")

    analyzer = TicketAnalyzer()

    viv_file = st.file_uploader("העלה את קובץ הכרטיסים הראשי (CSV או Excel)", type=['csv', 'xlsx'])
    fortress_file = st.file_uploader("העלה את קובץ נתוני הכניסה (CSV או Excel)", type=['csv', 'xlsx'])

    if viv_file and fortress_file:
        if analyzer.load_files(viv_file, fortress_file):
            if st.button("נתח כרטיסים"):
                if analyzer.analyze_tickets():
                    analyzer.display_results()

if __name__ == "__main__":
    main()
