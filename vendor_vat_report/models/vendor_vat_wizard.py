import base64
import io
from odoo.exceptions import ValidationError
from odoo.tools.misc import xlwt
from odoo import fields, models, api, _

column_row_style = xlwt.easyxf('font:height 200;align: horiz center;font:color black;'
                               ' font:bold True;')
column_heading_style = xlwt.easyxf(
    'font:height 200;align: horiz center;font:bold True;pattern: pattern solid, fore_color yellow;')
column_total_style = xlwt.easyxf(
    'font:height 200;align: horiz center;font:bold True;pattern: pattern solid, fore_color gray25 ;')


class VendorVatWizard(models.TransientModel):
    _name = 'vendor.vat.wizard'
    _description = 'Vendor Vat Wizard'

    date_from = fields.Date(string="From", required=False, )
    date_to = fields.Date(string="To", required=False, )
    product_report_file = fields.Binary('Stock Product Order Report')
    file_name = fields.Char('File Name')
    product_printed = fields.Boolean('Report Printed')

    def print_excel_report(self):
        self.product_printed = True
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Vendor Vat', cell_overwrite_ok=True)
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        worksheet.row(2).height = 500
        worksheet.row(3).height = 500
        report_head = 'ضريبة القيمة المضافة المشتريات '
        worksheet.write_merge(0, 0, 0, 9, report_head, xlwt.easyxf(
            'font:height 300; align: vertical center; align: horiz center;borders: top thin,bottom thin'))
        worksheet.write_merge(1, 1, 0, 9, 'العملات:ريال سعودي', xlwt.easyxf(
            'font:height 300; align: vertical center; align: horiz center;borders: top thin,bottom thin'))
        date_title = 'اعتباراً من '
        date_title += str(self.date_from) if self.date_from else ' - '
        date_title +='إلى'
        date_title += str(self.date_to) if self.date_to else ' - '
        worksheet.write_merge(2, 2, 0, 9,date_title, xlwt.easyxf(
            'font:height 300; align: vertical center; align: horiz center;borders: top thin,bottom thin'))
        ta_row = 3
        worksheet.write(ta_row, 0, _('رقم الفاتورة'), column_heading_style)
        worksheet.write(ta_row, 1, _('صافي القيمة'), column_heading_style)
        worksheet.write(ta_row, 2, _(' الحسميات'), column_heading_style)
        worksheet.write(ta_row, 3, _('قيمة الضريبة'), column_heading_style)
        worksheet.write(ta_row, 4, _('القيمة'), column_heading_style)
        worksheet.write(ta_row, 5, _('الرقم الضريبي'), column_heading_style)
        worksheet.write(ta_row, 6, _('طبيعة الشراء'), column_heading_style)
        worksheet.write(ta_row, 7, _('ًاسم الزبون'), column_heading_style)
        worksheet.write(ta_row, 8, _('تـاريـخ السنـد'), column_heading_style)
        worksheet.write(ta_row, 9, _('الرقم'), column_heading_style)
        worksheet.col(0).width = 6000
        worksheet.col(1).width = 4000
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 6000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 4000
        worksheet.col(6).width = 4000
        worksheet.col(7).width = 6000
        worksheet.col(8).width = 4000
        worksheet.col(9).width = 2000
        worksheet.row(3).height = 500
        count =0
        domain = [('move_type','=','in_invoice')]
        if self.date_from:
            domain.append(('date','>=',self.date_from))
        if self.date_to:
            domain.append(('date','<=',self.date_to))
        moves = self.env['account.move'].search(domain)
        row = 4
        amount_total= 0
        total_discount =0
        amount_tax = 0
        amount_untaxed = 0
        if moves:
            for move in moves:
                count += 1
                discount = 0.0
                for line in move.invoice_line_ids:
                    discount += (((line.quantity * line.price_unit)*line.discount)/100)

                worksheet.write(row, 0, move.name, column_row_style)
                worksheet.write(row, 1, move.amount_total, column_row_style)
                worksheet.write(row, 2, discount, column_row_style)
                worksheet.write(row, 3,move.amount_tax, column_row_style)
                worksheet.write(row, 4, move.amount_untaxed, column_row_style)
                worksheet.write(row, 5,  move.partner_id.vat if move.partner_id.vat else '', column_row_style)
                worksheet.write(row, 6, move.po_type if move.po_type else '', column_row_style)
                worksheet.write(row, 7, move.partner_id.name, column_row_style)
                worksheet.write(row, 8, str(move.invoice_date) if move.invoice_date else ' ', column_row_style)
                worksheet.write(row, 9, count, column_row_style)
                row += 1
                amount_total += move.amount_total
                amount_tax += move.amount_tax
                amount_untaxed += move.amount_untaxed
                total_discount += discount
            worksheet.write_merge(row,row, 5,9, 'الاجمـــالــي', column_total_style)
            worksheet.write(row, 0, '', column_total_style)
            worksheet.write(row, 1, amount_total, column_total_style)
            worksheet.write(row, 2, total_discount, column_total_style)
            worksheet.write(row, 3, amount_tax, column_total_style)
            worksheet.write(row, 4, amount_untaxed, column_total_style)

            for wizard in self:
                fp = io.BytesIO()
                workbook.save(fp)
                excel_file = base64.b64encode(fp.getvalue())
                wizard.product_report_file = excel_file
                wizard.file_name = 'Stock Product Report.xls'
                fp.close()
                return {
                    'view_mode': 'form',
                    'res_id': wizard.id,
                    'res_model': 'vendor.vat.wizard',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self.env.context,
                    'target': 'new',
                }
        else:
            raise ValidationError(_("Not Found Any Product On That Warehouse."))

    def print_other_report(self):
        return {
            'view_mode': 'form',
            'res_model': 'vendor.vat.wizard',
            'name': 'Stock Product Report',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }

    @api.constrains('date_from', 'date_to')
    def validate_dates(self):
        for rec in self:
            if rec.date_to and rec.date_from:
                if rec.date_to < rec.date_from:
                    raise ValidationError(_('Date to should be greater than date from.'))
