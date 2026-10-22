import Foundation
import AVFoundation
import AppKit

let directory = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])
let files = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil).filter { $0.pathExtension == "png" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [AVVideoCodecKey:AVVideoCodecType.h264, AVVideoWidthKey:240, AVVideoHeightKey:240])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32ARGB,kCVPixelBufferWidthKey as String:240,kCVPixelBufferHeightKey as String:240])
writer.add(input)
writer.startWriting(); writer.startSession(atSourceTime: .zero)
for (index,file) in files.enumerated() {
    while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval:0.01) }
    let img=NSImage(contentsOf:file)!.cgImage(forProposedRect:nil, context:nil,hints:nil)!
    var buffer:CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil,adaptor.pixelBufferPool!,&buffer)
    CVPixelBufferLockBaseAddress(buffer!,[])
    let context=CGContext(data:CVPixelBufferGetBaseAddress(buffer!),width:240,height:240,bitsPerComponent:8,bytesPerRow:CVPixelBufferGetBytesPerRow(buffer!),space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.noneSkipFirst.rawValue)!
    context.draw(img,in:CGRect(x:0,y:0,width:240,height:240))
    CVPixelBufferUnlockBaseAddress(buffer!,[])
    guard adaptor.append(buffer!,withPresentationTime:CMTime(value:Int64(index*170),timescale:1000)) else { fatalError("append failed") }
}
input.markAsFinished()
let done=DispatchSemaphore(value:0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed else { fatalError(String(describing:writer.error)) }
print(output.path)
