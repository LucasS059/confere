// OCR local via Apple Vision. Este modelo de OCR não é o GPT experimental.
import AppKit
import Foundation
import PDFKit
import Vision

struct Line: Codable {
    let text: String
    let confidence: Float
    let x: CGFloat
    let y: CGFloat
    let width: CGFloat
    let height: CGFloat
}
struct Page: Codable {
    let number: Int
    let width: CGFloat
    let height: CGFloat
    let lines: [Line]
}

guard CommandLine.arguments.count == 3 else {
    fatalError("Uso: swift ocr_macos.swift entrada.pdf diretório-de-páginas")
}
let input = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
guard let document = PDFDocument(url: input), !document.isLocked else {
    fatalError("PDF inválido ou protegido")
}
var pages: [Page] = []
for index in 0..<document.pageCount {
    try autoreleasepool {
        guard let page = document.page(at: index) else { fatalError("Página ausente") }
        let bounds = page.bounds(for: .mediaBox)
        let scale: CGFloat = 3
        guard let context = CGContext(
            data: nil, width: Int(bounds.width * scale), height: Int(bounds.height * scale),
            bitsPerComponent: 8, bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ) else { fatalError("Não foi possível renderizar") }
        context.setFillColor(NSColor.white.cgColor)
        context.fill(CGRect(x: 0, y: 0, width: bounds.width * scale, height: bounds.height * scale))
        context.scaleBy(x: scale, y: scale)
        context.translateBy(x: -bounds.minX, y: -bounds.minY)
        page.draw(with: .mediaBox, to: context)
        guard let image = context.makeImage() else { fatalError("Imagem ausente") }
        let bitmap = NSBitmapImageRep(cgImage: image)
        try bitmap.representation(using: .png, properties: [:])!.write(
            to: output.appendingPathComponent("page-\(index + 1).png"), options: .atomic
        )
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["pt-BR", "en-US"]
        request.usesLanguageCorrection = true
        try VNImageRequestHandler(cgImage: image).perform([request])
        let lines: [Line] = (request.results ?? []).compactMap { observation in
            guard let candidate = observation.topCandidates(1).first else { return nil }
            let box = observation.boundingBox
            return Line(text: candidate.string, confidence: candidate.confidence,
                        x: box.minX, y: box.minY, width: box.width, height: box.height)
        }
        pages.append(Page(number: index + 1, width: bounds.width, height: bounds.height, lines: lines))
        fputs("OCR: página \(index + 1)/\(document.pageCount)\n", stderr)
    }
}
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
FileHandle.standardOutput.write(try encoder.encode(pages))
