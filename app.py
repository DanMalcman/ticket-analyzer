import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

class TicketAnalyzer:
    def __init__(self):
        self.df_viv = None
        self.df_fortress = None
        self.df_merged = None
        self.results = {}

    def upload_main_file(self):
        uploaded_file = st.file_uploader("העלה את קובץ הכרטיסים הראשי (חובה עמודת 'barcode')", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    self.df_viv = pd.read_csv(uploaded_file)
                else:
                    self.df_viv = pd.read_excel(uploaded_file)

                if 'barcode' not in self.df_viv.columns:
                    st.error("שגיאה: חסרה עמודת barcode בקובץ שהעלית.")
                    return False

                st.success(f"טעינה הצליחה! נמצאו {len(self.df_viv)} כרטיסים.")
                return True
            except Exception as e:
                st.error(f"שגיאה בקריאת הקובץ: {e}")
        return False

    def upload_entry_file(self):
        uploaded_file = st.file_uploader("העלה את קובץ נתוני הכניסה (חובה עמודת 'Barcode')", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    self.df_fortress = pd.read_csv(uploaded_file)
                else:
                    self.df_fortress = pd.read_excel(uploaded_file)

                if 'Barcode' not in self.df_fortress.columns:
                    st.error("שגיאה: חסרה עמודת Barcode בקובץ שהעלית.")
                    return False

                st.success(f"טעינה הצליחה! נמצאו {len(self.df_fortress)} רשומות כניסה.")
                return True
            except Exception as e:
                st.error(f"שגיאה בקריאת הקובץ: {e}")
        return False

    def analyze_tickets(self):
        if self.df_viv is None or self.df_fortress is None:
            st.error("יש להעלות את שני הקבצים לפני הניתוח.")
            return False

        self.df_merged = pd.merge(
            self.df_viv, self.df_fortress, left_on='barcode', right_on='Barcode', how='left'
        )
        self.df_merged['Entered to the game?'] = self.df_merged['Barcode'].apply(
            lambda x: 'V' if pd.notna(x) else 'X'
        )

        entered = self.df_merged[self.df_merged['Entered to the game?'] == 'V']
        not_entered = self.df_merged[self.df_merged['Entered to the game?'] == 'X']

        self.results = {
            'total_tickets': len(self.df_merged),
            'total_entered': len(entered),
            'total_not_entered': len(not_entered),
            'entry_rate': f"{(len(entered) / len(self.df_merged) * 100):.1f}%"
        }
        return True

    def display_results(self):
        if not self.results:
            st.warning("אין תוצאות. יש לבצע ניתוח קודם.")
            return

        st.subheader("📊 תוצאות ניתוח")
        st.success(f'סה"כ נכנסו: {self.results["total_entered"]} מתוך {self.results["total_tickets"]} ({self.results["entry_rate"]})')
        st.error(f'סה"כ לא נכנסו: {self.results["total_not_entered"]} מתוך {self.results["total_tickets"]}')

        # Pie chart
        fig, ax = plt.subplots()
        labels = ['נכנסו', 'לא נכנסו']
        sizes = [self.results['total_entered'], self.results['total_not_entered']]
        colors = ['#4CAF50', '#F44336']
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

def main():
    st.set_page_config(page_title="Ticket Entry Analyzer", page_icon="🎟️")
    st.title("🎟️ מנתח כניסות לאירוע")

    analyzer = TicketAnalyzer()
    if analyzer.upload_main_file():
        if analyzer.upload_entry_file():
            if analyzer.analyze_tickets():
                analyzer.display_results()

if __name__ == '__main__':
    main()

