package com.backend.careercatalyst.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.io.ByteArrayInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

@Service
public class FileStorageService {
    private final Path fileStorageLocation;

    /**
     * Constructor that sets up the directory for storing generated resume files.
     * The path is read from the 'application.properties' file.
     */
    public FileStorageService(@Value("${file.storage.path}") String storagePath) {
        this.fileStorageLocation = Paths.get(storagePath).toAbsolutePath().normalize();
        try {
            Files.createDirectories(this.fileStorageLocation);
        } catch (Exception ex) {
            throw new RuntimeException("Could not create the directory where the generated files will be stored.", ex);
        }
    }

    /**
     * Unzips the byte array from the Python service and saves the files
     * into a unique directory named with a session ID.
     *
     * @param zipData The byte array of the zip file.
     * @return The unique session ID for this set of files.
     * @throws IOException if an I/O error occurs.
     */
    public String saveAndUnzipFiles(byte[] zipData) throws IOException {
        String sessionId = UUID.randomUUID().toString();
        Path sessionPath = this.fileStorageLocation.resolve(sessionId);
        Files.createDirectories(sessionPath);

        try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(zipData))) {
            ZipEntry zipEntry = zis.getNextEntry();
            while (zipEntry != null) {
                // Prevent Zip Slip vulnerability
                String fileName = StringUtils.cleanPath(zipEntry.getName());
                Path newFilePath = sessionPath.resolve(fileName);
                
                // Ensure the file is being created within the session directory
                if (!newFilePath.getParent().equals(sessionPath)) {
                    throw new IOException("Invalid file path in zip entry: " + fileName);
                }

                try (FileOutputStream fos = new FileOutputStream(newFilePath.toFile())) {
                    byte[] buffer = new byte[1024];
                    int len;
                    while ((len = zis.read(buffer)) > 0) {
                        fos.write(buffer, 0, len);
                    }
                }
                zipEntry = zis.getNextEntry();
            }
            zis.closeEntry();
        }
        return sessionId;
    }

    /**
     * Loads a specific file (e.g., resume.pdf) from a session directory.
     *
     * @param sessionId The unique ID for the session.
     * @param fileName The name of the file to load.
     * @return A Resource object for the requested file.
     */
    public Resource loadFileAsResource(String sessionId, String fileName) {
        try {
            Path filePath = this.fileStorageLocation.resolve(sessionId).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());
            if (resource.exists()) {
                return resource;
            } else {
                throw new RuntimeException("File not found: " + fileName);
            }
        } catch (MalformedURLException ex) {
            throw new RuntimeException("File not found: " + fileName, ex);
        }
    }
}