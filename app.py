import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

class TicketAnalyzer:
    def __init__(self):
        self.df_viv = None
        self.df_fortress = None
        self.df_merged = None
        self.results = {}

    def upload_files(self):
        st.header("📁 העלאת קבצים")

        viv_file = st.file_uploader("שלב 1️⃣ העלה את קובץ הכרטיסים מויוניו (CSV / Excel)", type=['csv', 'xlsx'], key='viv')
        fortress_file = st.file_uploader("שלב 2️⃣ העלה את דוח הכניסות מפורטרס (CSV / Excel)", type=['csv', 'xlsx'], key='fortress')

        if viv_file and fortress_file:
            try:
                self.df_viv = pd.read_csv(viv_file) if viv_file.name.endswith('.csv') else pd.read_excel(viv_file)
                self.df_fortress = pd.read_csv(fortress_file) if fortress_file.name.endswith('.csv') else pd.read_excel(fortress_file)

                if 'barcode' not in self.df_viv.columns:
                    st.error("⚠️ קובץ הכרטיסים חייב לכלול עמודת 'barcode'")
                    return False
                if 'Barcode' not in self.df_fortress.columns:
                    st.error("⚠️ דוח הכניסות חייב לכלול עמודת 'Barcode'")
                    return False

                return True
            except Exception as e:
                st.error(f"שגיאה בקריאת הקבצים: {e}")
                return False
        return False

    def analyze(self):
        if self.df_viv is None or self.df_fortress is None:
            return False

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
            st.error(f"שגיאה בניתוח הכרטיסים: {e}")
            return False

    def display_results(self):
        if not self.results:
            st.warning("אין תוצאות. יש לבצע ניתוח קודם.")
            return

        st.header("📊 תוצאות ניתוח")
        st.success(f"סה״כ נכנסו: {self.results['total_entered']} מתוך {self.results['total_tickets']} ({self.results['entry_rate']})")
        st.error(f"סה״כ לא נכנסו: {self.results['total_not_entered']} מתוך {self.results['total_tickets']}")

        # Pie chart
        fig, ax = plt.subplots()
        labels = ['נכנסו', 'לא נכנסו']
        sizes = [self.results['total_entered'], self.results['total_not_entered']]
        colors = ['#4CAF50', '#F44336']
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

        if self.results['has_ticket_name']:
            st.subheader("📌 פירוט לפי סוג כרטיס")
            st.write(f"🎟️ כרטיסים רגילים שנכנסו: {self.results['entered_regular']}")
            st.write(f"🎟️ מנויים שנכנסו: {self.results['entered_season']}")
            st.write(f"🚪 כרטיסים רגילים שלא נכנסו: {self.results['not_entered_regular']}")
            st.write(f"🚪 מנויים שלא נכנסו: {self.results['not_entered_season']}")

        st.subheader("📋 טבלת כרטיסים מלאה")
        st.dataframe(self.df_merged)

def main():
    st.set_page_config(page_title="🎫 ניתוח כרטיסים לאירוע", layout="wide")
    st.title("🎫 אפליקציית ניתוח כרטיסים לאירוע")

    analyzer = TicketAnalyzer()

    if analyzer.upload_files():
        if st.button("🔍 בצע ניתוח"):
            if analyzer.analyze():
                analyzer.display_results()
            else:
                st.error("ניתוח נכשל, יש לבדוק את הקבצים.")

if __name__ == "__main__":
    main()
