import QtQuick 2.7
import calamares.slideshow 1.0

Presentation {
    id: presentation
    function next() { presentation.goToNextSlide(); }
    function previous() { presentation.goToPreviousSlide(); }

    Slide {
        id: slide1
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            text: qsTr("Welcome to OpenNAS-Lite\nOpen-source NAS for older hardware.")
            font.pointSize: 18
            color: "#e8eef5"
        }
    }
    Slide {
        id: slide2
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            text: qsTr("Choose a storage profile, then partition disks.\nDestructive steps require confirmation.")
            font.pointSize: 16
            color: "#e8eef5"
        }
    }
}
