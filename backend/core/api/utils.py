import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from django.http import FileResponse


def download_pdf(ingredients):
    """Запись данных в pdf-файл."""
    registerFont(
        TTFont(
            'American Typewriter',
            '/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc',
        )
    )
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
    textob = p.beginText()
    textob.setTextOrigin(cm * 2, cm * 2)
    textob.setFont('American Typewriter', 24)
    textob.textLine('Список ингредиентов для покупки.')
    textob.setFont('American Typewriter', 14)
    for name, amount, unit in ingredients:
        textob.textLine(f'{name} {amount} {unit}.')
    p.setTitle('Download')
    p.drawText(textob)
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='shop.pdf')
