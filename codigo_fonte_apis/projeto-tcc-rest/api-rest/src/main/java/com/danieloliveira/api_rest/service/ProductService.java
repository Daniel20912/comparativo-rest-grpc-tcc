package com.danieloliveira.api_rest.service;

import com.danieloliveira.api_rest.dto.ProductDTO;
import com.danieloliveira.api_rest.model.Product;
import com.danieloliveira.api_rest.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    public Product create(ProductDTO dto) {
        Product product = toProduct(dto);
        productRepository.save(product);
        return product;
    }

    public Product findById(long id) {
        return productRepository.findById(id);
    }

    public Product updateProduct(Long id, ProductDTO dto) {
        if (productRepository.findById(id) != null) {
            return setProductAttributes(id, dto);
        }
        return null;
    }

    public void delete(long id) {
        productRepository.delete(id);
    }

    /// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    private Product toProduct(ProductDTO dto) {
        Long id = productRepository.incrementSequence();
        Product product = new Product();
        product.setId(id);
        product.setName(dto.getName());
        product.setDescription(dto.getDescription());
        product.setPrice(dto.getPrice());
        product.setCategory(dto.getCategory());
        product.setStock(dto.getStock());
        product.setCreatedAt(LocalDateTime.now());

        return product;
    }

    private Product setProductAttributes(Long id, ProductDTO dto) {
        Product product = productRepository.findById(id);
        product.setName(dto.getName());
        product.setDescription(dto.getDescription());
        product.setPrice(dto.getPrice());
        product.setStock(dto.getStock());
        product.setCategory(dto.getCategory());

        return product;
    }
}
