"""
Resume Optimizer - Local Desktop Application
Tkinter-based GUI for deterministic resume optimization
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from pathlib import Path

from json_parser import parse_replacement_payload
from docx_handler import extract_text, apply_replacements


class ResumeOptimizerApp:
    """Main tkinter application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Optimizer")
        self.root.geometry("1000x900")
        
        self.resume_path = None
        self.resume_text = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup tkinter UI"""
        # Title
        title = ttk.Label(self.root, text="Resume Optimizer", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        subtitle = ttk.Label(self.root, text="Local, offline, no API", font=("Arial", 10))
        subtitle.pack()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === STEP 1: RESUME UPLOAD ===
        step1_label = ttk.Label(main_frame, text="Step 1: Upload Resume (.docx)", font=("Arial", 11, "bold"))
        step1_label.pack(anchor="w", pady=(10, 5))
        
        resume_btn_frame = ttk.Frame(main_frame)
        resume_btn_frame.pack(fill="x", pady=5)
        
        self.resume_btn = ttk.Button(
            resume_btn_frame,
            text="📁 Select Resume",
            command=self._select_resume
        )
        self.resume_btn.pack(side="left", padx=5)
        
        self.resume_status = ttk.Label(resume_btn_frame, text="No file selected", foreground="red")
        self.resume_status.pack(side="left", padx=10)
        
        # === STEP 2: JSON PAYLOAD ===
        step2_label = ttk.Label(main_frame, text="Step 2: Paste JSON Replacement Payload", font=("Arial", 11, "bold"))
        step2_label.pack(anchor="w", pady=(15, 5))
        
        # Help text
        help_text = ttk.Label(
            main_frame,
            text="⚠️ IMPORTANT: match_anchor must be the FULL paragraph text (copy entire bullet/summary from resume)",
            font=("Arial", 9),
            foreground="red"
        )
        help_text.pack(anchor="w", pady=(0, 5))
        
        self.json_text = scrolledtext.ScrolledText(main_frame, height=12, width=120)
        self.json_text.pack(fill="both", expand=True, pady=5)
        self.json_text.insert("1.0", self._example_json())
        
        # === CONTROL BUTTONS ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=15)
        
        self.optimize_btn = ttk.Button(
            btn_frame,
            text="🚀 Optimize Resume",
            command=self._optimize,
            state="disabled"
        )
        self.optimize_btn.pack(side="left", padx=5)
        
        reset_btn = ttk.Button(btn_frame, text="Clear All", command=self._reset)
        reset_btn.pack(side="left", padx=5)
        
        # === OUTPUT ===
        output_label = ttk.Label(main_frame, text="Status & Output", font=("Arial", 11, "bold"))
        output_label.pack(anchor="w", pady=(15, 5))
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=8, width=120)
        self.output_text.pack(fill="both", expand=True, pady=5)
        self.output_text.config(state="disabled")
        
        self._log("✨ Ready to optimize\n")
    
    def _example_json(self) -> str:
        """Return example JSON"""
        return """{
  "summary_replacement": {
    "match_anchor": "MBA candidate and strategy-driven operations professional with experience supporting revenue, growth, and go-to-market execution through analytics, systems, and cross-functional leadership. Proven track record of driving performance through KPI reporting, process optimization, enablement programs, and scalable operating models across consulting, technology, healthcare, and global retail environments. Strong analytical foundation with hands-on experience in Excel, SQL, Tableau, SAP, and CRM-enabled workflows, partnering closely with sales, marketing, finance, product, and leadership teams to improve visibility, efficiency, and decision-making.",
    "replacement_text": "MBA candidate (Class of 2026) with 6+ years of international supply chain and logistics leadership, managing $50M–$240M global operations across distribution, transportation, and supplier networks. Proven track record of delivering multi-million-dollar cost savings, leading cross-functional transformations, and building data-driven operating models across retail, consulting, and healthcare environments."
  },
  "bullet_replacements": [
    {
      "match_anchor": "Built a go-to-market supply and pricing model by evaluating international suppliers, cost structures, and margin scenarios, enabling a successful product launch with a 60% gross margin",
      "replacement_text": "Developed a supplier sourcing and margin optimization model by analyzing international cost structures and pricing scenarios, enabling product launch at 60% gross margin"
    },
    {
      "match_anchor": "Managed an 8,000+ container network across 15 international warehouses within a $240M operation, applied route optimization software, and led a 35-person cross-functional team to reduce freight costs by $400K annually",
      "replacement_text": "Managed an 8,000+ container global transportation network within a $240M operation, leading a 35-person cross-functional team and deploying network optimization strategies to reduce annual spend by $400K"
    }
  ]
}
"""
    
    def _select_resume(self):
        """File dialog for resume"""
        file_path = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.resume_path = file_path
                self.resume_text = extract_text(file_path)
                
                filename = Path(file_path).name
                self.resume_status.config(text=f"✅ {filename}", foreground="green")
                self._log(f"✅ Loaded: {filename}\n")
                
                self._check_ready()
                
            except Exception as e:
                self._log(f"❌ Error loading resume: {str(e)}\n")
                messagebox.showerror("Error", f"Failed to load resume: {str(e)}")
    
    def _check_ready(self):
        """Check if ready to optimize"""
        json_text = self.json_text.get("1.0", "end").strip()
        has_resume = self.resume_path is not None
        has_json = json_text and json_text != self._example_json()
        
        if has_resume and has_json:
            self.optimize_btn.config(state="normal")
        else:
            self.optimize_btn.config(state="disabled")
    
    def _optimize(self):
        """Main optimization workflow"""
        if not self.resume_path:
            messagebox.showerror("Error", "Please select a resume")
            return
        
        json_text = self.json_text.get("1.0", "end").strip()
        if not json_text:
            messagebox.showerror("Error", "Please paste JSON payload")
            return
        
        self._log("🔄 Starting optimization...\n")
        self.optimize_btn.config(state="disabled")
        
        try:
            # Step 1: Parse JSON
            self._log("📋 Parsing JSON...\n")
            payload = parse_replacement_payload(json_text)
            self._log("✅ JSON valid\n")
            
            # Step 2: Apply replacements
            self._log("📝 Applying replacements...\n")
            success, message = apply_replacements(self.resume_path, payload)
            
            if success:
                self._log(f"\n{message}\n")
                messagebox.showinfo("Success", message)
            else:
                self._log(f"\n{message}\n")
                messagebox.showerror("Error", message)
        
        except ValueError as e:
            self._log(f"\n❌ {str(e)}\n")
            messagebox.showerror("Error", str(e))
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._log(f"\n❌ {error_msg}\n")
            messagebox.showerror("Error", error_msg)
        
        finally:
            self.optimize_btn.config(state="normal")
    
    def _log(self, message: str):
        """Write to output"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", message)
        self.output_text.see("end")
        self.output_text.config(state="disabled")
    
    def _reset(self):
        """Reset app"""
        self.resume_path = None
        self.resume_text = None
        self.resume_status.config(text="No file selected", foreground="red")
        self.json_text.delete("1.0", "end")
        self.json_text.insert("1.0", self._example_json())
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        self.optimize_btn.config(state="disabled")
        self._log("✨ Application reset\n")


def main():
    root = tk.Tk()
    app = ResumeOptimizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
