// SPDX-License-Identifier: GPL-3.0-or-later
import QtQuick 2.7
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.3
import calamares 2.0

Item {
    id: root
    property string chosenProfile: "standard"

    function onActivate() {
        var hw = calamares.global.storage.value("opennasHwCheck");
        if (!hw) {
            calamares.global.storage.set("opennasHwCheck", {});
        }
        calamares.global.storage.set("opennasProfile", chosenProfile);
    }

    function onLeaveNext() {
        calamares.global.storage.set("opennasProfile", chosenProfile);
        return true;
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 12

        Label {
            text: qsTr("Storage and feature profile")
            font.pointSize: 16
            font.bold: true
        }

        Label {
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            text: qsTr("Minimal suits 2 GB RAM (no Docker by default). Standard needs ~4 GB. Full enables ZFS/VM options when hardware allows.")
        }

        ComboBox {
            id: profileBox
            Layout.fillWidth: true
            model: ["minimal", "standard", "full"]
            currentIndex: 1
            onCurrentTextChanged: root.chosenProfile = currentText
        }

        Label {
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            text: qsTr("RAID and pool layout are configured in the next step. Destructive disk operations always require confirmation.")
            font.italic: true
        }
    }
}
