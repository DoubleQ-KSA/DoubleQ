odoo.define('vendor_vat_report.ReceiptScreenInherit', function(require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const ReceiptScreenInherit = ReceiptScreen =>
        class extends ReceiptScreen {
            async handleAutoPrint() {
                if (this._shouldAutoPrint()) {
                    await this.printReceipt();
                    if (this.currentOrder._printed && this._shouldCloseImmediately()) {
                        this.whenClosing();
                    }
                }
                  const order = this.currentOrder;
                    const orderName = order.get_name();
                    const order_server_id = this.env.pos.validated_orders_name_server_id_map[orderName];
                    await this.env.pos.do_action('vendor_vat_report.pos_order_report', {
                        additional_context: {
                            active_ids: [order_server_id],
                        },
                    });
            }
        };

    Registries.Component.extend(ReceiptScreen, ReceiptScreenInherit);

    return ReceiptScreen;
});
