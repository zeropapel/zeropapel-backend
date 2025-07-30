import os
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import black, gray
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from flask import current_app
import tempfile
import uuid
from datetime import datetime

def generate_qr_code(data, size=100):
    """Generate QR code and return file path"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        qr_filename = f"qr_{uuid.uuid4().hex}.png"
        qr_path = os.path.join(temp_dir, qr_filename)
        
        img.save(qr_path)
        return qr_path
        
    except Exception as e:
        current_app.logger.error(f"Error generating QR code: {str(e)}")
        return None

def create_signature_footer(signature_data, qr_code_path=None):
    """Create a signature footer PDF overlay"""
    try:
        # Create a temporary PDF with signature footer
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Footer dimensions
        footer_height = 1.5 * inch
        page_width, page_height = A4
        
        # Draw footer background
        c.setFillColor(gray)
        c.rect(0, 0, page_width, footer_height, fill=1, stroke=0)
        
        # Set text color
        c.setFillColor(black)
        
        # Add signature information
        y_pos = footer_height - 0.3 * inch
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.5 * inch, y_pos, "DOCUMENTO ASSINADO ELETRONICAMENTE")
        
        y_pos -= 0.2 * inch
        c.setFont("Helvetica", 8)
        
        # Signature details
        details = [
            f"Assinado por: {signature_data.get('signer_email', 'N/A')}",
            f"Data/Hora: {signature_data.get('signed_at', 'N/A')}",
            f"IP: {signature_data.get('ip_address', 'N/A')}",
            f"ID da Assinatura: {signature_data.get('signature_id', 'N/A')}"
        ]
        
        for detail in details:
            c.drawString(0.5 * inch, y_pos, detail)
            y_pos -= 0.15 * inch
        
        # Add QR code if provided
        if qr_code_path and os.path.exists(qr_code_path):
            try:
                qr_size = 0.8 * inch
                qr_x = page_width - qr_size - 0.5 * inch
                qr_y = 0.2 * inch
                c.drawImage(qr_code_path, qr_x, qr_y, qr_size, qr_size)
                
                # Add QR code label
                c.setFont("Helvetica", 6)
                c.drawString(qr_x, qr_y - 0.15 * inch, "Verificar documento")
                
            except Exception as e:
                current_app.logger.warning(f"Could not add QR code to footer: {str(e)}")
        
        c.save()
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        current_app.logger.error(f"Error creating signature footer: {str(e)}")
        return None

def add_signature_to_pdf(input_path, output_path, signature_data, qr_code_path=None):
    """Add signature footer and QR code to PDF"""
    try:
        # Read the original PDF
        with open(input_path, 'rb') as input_file:
            reader = PdfReader(input_file)
            writer = PdfWriter()
            
            # Create signature footer
            footer_buffer = create_signature_footer(signature_data, qr_code_path)
            if not footer_buffer:
                return False
            
            footer_reader = PdfReader(footer_buffer)
            footer_page = footer_reader.pages[0]
            
            # Add footer to each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                
                # Merge footer with page
                page.merge_page(footer_page)
                writer.add_page(page)
            
            # Write the output PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error adding signature to PDF: {str(e)}")
        return False

def extract_pdf_text(pdf_path):
    """Extract text from PDF for indexing/searching"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        current_app.logger.error(f"Error extracting PDF text: {str(e)}")
        return ""

def get_pdf_page_count(pdf_path):
    """Get number of pages in PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        current_app.logger.error(f"Error getting PDF page count: {str(e)}")
        return 0

def validate_pdf_file(pdf_path):
    """Validate if file is a valid PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            # Try to read the first page
            if len(reader.pages) > 0:
                reader.pages[0]
            return True
    except Exception as e:
        current_app.logger.error(f"PDF validation failed: {str(e)}")
        return False

def convert_docx_to_pdf_advanced(docx_path, pdf_path):
    """Advanced DOCX to PDF conversion (placeholder for future implementation)"""
    try:
        # This is a placeholder for advanced DOCX to PDF conversion
        # In production, you could use:
        # 1. python-docx + reportlab for basic conversion
        # 2. LibreOffice headless mode
        # 3. External service like Pandoc
        # 4. Commercial API like Aspose or GroupDocs
        
        current_app.logger.warning("Advanced DOCX to PDF conversion not implemented")
        
        # For now, just copy the file (this is NOT a real conversion)
        import shutil
        shutil.copy2(docx_path, pdf_path)
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"DOCX to PDF conversion error: {str(e)}")
        return False

def add_watermark_to_pdf(input_path, output_path, watermark_text="DRAFT"):
    """Add watermark to PDF (useful for draft documents)"""
    try:
        # Create watermark
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Set watermark properties
        c.setFillColor(gray)
        c.setFont("Helvetica-Bold", 50)
        
        # Rotate and position watermark
        c.saveState()
        c.translate(A4[0]/2, A4[1]/2)
        c.rotate(45)
        c.drawCentredText(0, 0, watermark_text)
        c.restoreState()
        
        c.save()
        buffer.seek(0)
        
        # Apply watermark to PDF
        with open(input_path, 'rb') as input_file:
            reader = PdfReader(input_file)
            writer = PdfWriter()
            
            watermark_reader = PdfReader(buffer)
            watermark_page = watermark_reader.pages[0]
            
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error adding watermark to PDF: {str(e)}")
        return False

def create_signature_certificate(signature_data):
    """Create a signature certificate PDF"""
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredText(A4[0]/2, A4[1] - 2*inch, "CERTIFICADO DE ASSINATURA ELETRÔNICA")
        
        # Content
        y_pos = A4[1] - 3*inch
        c.setFont("Helvetica", 12)
        
        certificate_data = [
            f"Documento: {signature_data.get('document_filename', 'N/A')}",
            f"Assinado por: {signature_data.get('signer_email', 'N/A')}",
            f"Data/Hora: {signature_data.get('signed_at', 'N/A')}",
            f"Endereço IP: {signature_data.get('ip_address', 'N/A')}",
            f"Localização: {signature_data.get('geolocation', 'N/A')}",
            f"ID da Assinatura: {signature_data.get('signature_id', 'N/A')}",
            f"Hash SHA-256: {signature_data.get('document_hash', 'N/A')}"
        ]
        
        for data in certificate_data:
            c.drawString(inch, y_pos, data)
            y_pos -= 0.3*inch
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredText(A4[0]/2, inch, f"Certificado gerado em {datetime.utcnow().isoformat()}")
        
        c.save()
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        current_app.logger.error(f"Error creating signature certificate: {str(e)}")
        return None

