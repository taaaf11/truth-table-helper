from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from docx.document import Document
from docx import Document as doc_create


@dataclass
class OperationBC:
    inputs: str
    gate_name: str
    operation_callable: Callable[[int, int], int] | Callable[[int], int]
    header: str | None = None
    
    def __post_init__(self):
        self.inputs = self.inputs.split("|")
        
    @property
    def header_name(self) -> str:
        return self.header or str(self)
    
    def do(self, values: list[int]) -> int:
        temp = values[0]
        for val in values[1:]:
            temp = self.operation_callable(temp, val)
        return temp
    
    def __str__(self):
        return f"{self.gate_name}{''.join(self.inputs)}"


AND = partial(OperationBC, gate_name="AND", operation_callable=lambda x, y: int(x == 1 and y == 1))
OR = partial(OperationBC, gate_name="OR", operation_callable=lambda x, y: int(x == 1 or y == 1))
NOT = partial(OperationBC, gate_name="NOT", operation_callable=lambda x: int(not x))

NAND = partial(OperationBC, gate_name="NAND", operation_callable=lambda x, y: int(not (x == 1 and y == 1)))
NOR = partial(OperationBC, gate_name="NOR", operation_callable=lambda x, y: int(not (x == 1 or y == 1)))

XOR = partial(OperationBC, gate_name="XOR", operation_callable=lambda x, y: int(x != y))
XNOR = partial(OperationBC, gate_name="XNOR", operation_callable=lambda x, y: int(x == y))


class Table:
    def __init__(self, inputs: str, *derived: OperationBC):
        self.inputs = inputs.split("|")
        self.derived = derived

        self.columns = []
        self.columns_index = {}
        
        self._construct_stored_columns()
        self._construct_derived_columns()
        
        self.names = [*self.inputs, *map(lambda x: x.header, self.derived)]
    
    @staticmethod
    def _construct_column(column_index: int, total_columns: int):
        if column_index == 0 or column_index > total_columns:
                raise Exception("column_index must be greater than 0 and less than total_columns")
        column = []

        total_entries = 2 ** total_columns
        # combinations = (2 ** (total_columns - column_index)) // 2
        combinations = (2 ** (total_columns - column_index))
        
        while len(column) < total_entries:
            for _ in range(combinations):
                column.append(0)
            else:
                for _ in range(combinations):
                    column.append(1)
                
        return column       

    
    def _construct_stored_columns(self):
        """
        Stored columns mean the "base" input variables
        from which all other values are calculated.
        """

        total_columns = len(self.inputs)
        
        for column_index in range(1, total_columns + 1):
            self.columns.append(Table._construct_column(column_index, total_columns))

            column_name = self.inputs[column_index - 1]
            self.columns_index[column_name] = self.columns[-1]
            
    def _construct_derived_columns(self):
        """
        Derived columns mean output columns whose values
        are calculated by applying gates on stored columns.
        """
        
        for derived_op in self.derived:
            column = []
            for row_index in range(2 ** len(self.inputs)):
                if derived_op.gate_name == "NOT":
                    final_value = int(not self.columns_index[derived_op.inputs[0]][row_index])
                    column.append(final_value)
                
                else:
                    formed_row = []
                    for input_ in derived_op.inputs:
                        value = self.columns_index[input_][row_index]
                        formed_row.append(value)
                    final_value = derived_op.do(formed_row)
                    column.append(final_value)
            
            self.columns.append(column)

            column_name = derived_op.header
            self.columns_index[column_name] = self.columns[-1]
    
    def to_docx_table(self, document: Document, filename_to_save: str):
        docx_table = document.add_table(rows=2 ** len(self.inputs) + 1, cols=len(self.columns))
        
        first_row_cells = docx_table.rows[0].cells
        for docx_col_index in range(len(self.columns)):
            first_row_cells[docx_col_index].text = self.names[docx_col_index]
        
        for docx_row_index in range(1, 2 ** len(self.inputs)):
            cells = docx_table.rows[docx_row_index].cells
            
            for docx_col_index in range(len(self.columns)):
                cells[docx_col_index].text = str(self.columns[docx_col_index][docx_row_index - 1])
            
        document.save(filename_to_save)
        

def make_document(filename: str, input_variables: str, *derived_columns: OperationBC):
    document = doc_create()
    # table = Table("A|B|C", NOT("A", header="NOT A"), NOT("B", header="NOT B"), AND("A|NOT B", header="A|NOT B")) 
    table = Table(input_variables, *derived_columns)
    table.to_docx_table(document, filename)