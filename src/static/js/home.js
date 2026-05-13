
var UserData = null;

// Ожидаемые входные данные: 
// Dr - ФИО Доктора
// Drug - Название лекарства
// Rec - Рекомендация применения
// DateStart - Дата начала
// DateEnd - Дата окончания
// ReceiptDrug - Является ли препорат рецептурным

function fillTable(){
	for (Data of UserData){
		const element = `
		<tr style="width: fit-content;">
			<td>${Data.Dr}</td>
			<td>${Data.Drug}</td>
			<td>${Data.Rec}</td>
			<td>${Data.DateStart}</td>
			<td>${Data.DateEnd}</td>
			<td>${Data.ReceiptDrug}</td>
		</tr>
		`
	}
}