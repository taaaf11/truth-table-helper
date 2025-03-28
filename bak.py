
# t = Table("x y", AND("x y", header='gg'), AND("x gg", header='hh'))
t = Table("A|B|C|D",
          # "Base"
          NOT("A", header="NOT A"),
          NOT("B", header="NOT B"),
          NOT("C", header="NOT C"),
          NOT("D", header="NOT D"),
          AND("NOT A|C", header="A̅C"),
          AND("NOT A|B|D", header="A̅BD"),

          # "Compound" (operands of OR (plus) )
          AND("A̅C|A̅BD", header="A̅C(A̅BD)"),
          AND("NOT A|B|NOT C|NOT D", header="A̅BC̅D̅"),
          AND("A|NOT B|C", header="AB̅C"),

          # Final 
          OR("A̅C(A̅BD)|A̅BC̅D̅|AB̅C", header="A̅C(A̅BD) + A̅BC̅D̅ + AB̅C")
)
t = Table("A|B|C", NOT("A", header="NOT A"), NOT("B", header="NOT B"), AND("A|NOT B", header="A|NOT B"), )                         
document = doc_create()
new_t = Table("A|B|C", NOT("A", header="NOT A"), NOT("B", header="NOT B"), AND("A|NOT B", header="A|NOT B")) 
print(t.columns[5])
t.to_docx_table(document, "idk.docx")
new_t.to_docx_table(document, "real.docx")
